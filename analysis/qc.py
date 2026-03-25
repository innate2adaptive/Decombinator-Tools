#!/usr/bin/env python3
"""
TCR repertoire analysis CLI tool.

Reads gzipped TSV files with immune repertoire data and produces:
  1. Pairwise Jaccard index heatmap
  2. Scatter plot: unique TCRs vs UMI counts per file
  3. Per-file histogram of av_UMI_cluster_size
"""

import argparse
import glob
import os
import sys
from pathlib import Path

import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

EXPECTED_COLUMNS = [
    "sequence_id", "v_call", "d_call", "j_call", "junction_aa",
    "duplicate_count", "sequence", "junction", "decombinator_id",
    "rev_comp", "productive", "sequence_aa", "cdr1_aa", "cdr2_aa",
    "vj_in_frame", "stop_codon", "conserved_c", "conserved_f",
    "sequence_alignment", "germline_alignment", "v_cigar", "d_cigar",
    "j_cigar", "av_UMI_cluster_size",
]


def scan_file(path: str) -> pl.LazyFrame:
    """Return a LazyFrame for a gzipped TSV file — no data read yet."""
    return pl.scan_csv(
        path,
        separator="\t",
        has_header=True,
        infer_schema_length=10_000,
        null_values=["", "NA", "None"],
    )


def resolve_files(patterns: list[str]) -> list[str]:
    """Expand glob patterns (including ** for recursive) into file paths."""
    paths = []
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        if not matches:
            print(f"Warning: no files matched pattern '{pattern}'", file=sys.stderr)
        paths.extend(matches)
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique


# ---------------------------------------------------------------------------
# Plot 1 – Jaccard heatmap
# ---------------------------------------------------------------------------

def jaccard(set_a: set, set_b: set) -> float:
    if not set_a and not set_b:
        return 1.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union else 0.0


def plot_jaccard_heatmap(
    file_data: dict[str, pl.LazyFrame],
    species_col: str,
    output_dir: str,
) -> None:
    """Compute pairwise Jaccard index and save a heatmap."""
    names = list(file_data.keys())
    n = len(names)

    # Collect only the species column per file — first collect point
    sets: dict[str, set] = {}
    for name, lf in file_data.items():
        col_names = lf.collect_schema().names()
        if species_col not in col_names:
            print(
                f"Warning: column '{species_col}' not found in '{name}'. "
                f"Available columns: {col_names}",
                file=sys.stderr,
            )
            sets[name] = set()
        else:
            sets[name] = set(
                lf.select(pl.col(species_col).drop_nulls())
                  .collect()[species_col]
                  .to_list()
            )

    # Compute pairwise matrix; NaN on the diagonal so the colour scale
    # reflects off-diagonal overlaps rather than being anchored to 1.0
    matrix = np.zeros((n, n))
    for i, a in enumerate(names):
        for j, b in enumerate(names):
            matrix[i, j] = jaccard(sets[a], sets[b])
    np.fill_diagonal(matrix, np.nan)
    # Dynamic upper bound: max of off-diagonal (non-NaN) values
    vmax = float(np.nanmax(matrix)) if not np.all(np.isnan(matrix)) else 1.0

    short_names = [Path(n).stem for n in names]

    figw = max(6, n * 0.8 + 2)
    figh = max(5, n * 0.7 + 1.5)
    # Scale cbar label/tick font proportionally to the shorter figure dimension
    cbar_fontsize = max(7, min(figw, figh) * 1.2)

    fig, ax = plt.subplots(figsize=(figw, figh))
    sns.heatmap(
        matrix,
        xticklabels=short_names,
        yticklabels=short_names,
        vmin=0,
        vmax=vmax,
        annot=n <= 20,
        fmt=".2f",
        cmap="viridis",
        linewidths=0.5,
        ax=ax,
        cbar_kws={"label": "Jaccard index"},
    )
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=cbar_fontsize)
    cbar.set_label("Jaccard index", size=cbar_fontsize)
    ax.set_title(f"Pairwise Jaccard index  (column: '{species_col}')", pad=12)
    plt.xticks(rotation=45, ha="right", fontsize=max(6, 10 - n // 5))
    plt.yticks(rotation=0, fontsize=max(6, 10 - n // 5))
    plt.tight_layout()

    out_path = os.path.join(output_dir, "jaccard_heatmap.png")
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {out_path}")


# ---------------------------------------------------------------------------
# Plot 2 – Scatter: unique TCRs vs UMI counts
# ---------------------------------------------------------------------------

def plot_scatter(
    file_data: dict[str, pl.LazyFrame],
    output_dir: str,
) -> None:
    """Scatter plot of unique TCR count vs total UMI count per file."""
    rows = []
    for name, lf in file_data.items():
        cols = lf.collect_schema().names()
        select_exprs = [pl.len().alias("n_rows")]
        if "duplicate_count" in cols:
            select_exprs.append(
                pl.col("duplicate_count").cast(pl.Float64, strict=False).sum().alias("umi_sum")
            )
        else:
            print(
                f"Warning: 'duplicate_count' not in '{name}', setting UMI sum to 0.",
                file=sys.stderr,
            )
            select_exprs.append(pl.lit(0.0).alias("umi_sum"))

        # Collect only the two aggregated scalars — second collect point
        result = lf.select(select_exprs).collect()
        rows.append({
            "file": Path(name).stem,
            "unique_tcrs": result["n_rows"][0],
            "umi_sum": result["umi_sum"][0],
        })

    summary = pl.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(
        data=summary.to_pandas(),
        x="unique_tcrs",
        y="umi_sum",
        ax=ax,
        s=80,
        color="steelblue",
        edgecolor="white",
        linewidth=0.6,
    )

    # Label each point
    for _, row in summary.to_pandas().iterrows():
        ax.annotate(
            row["file"],
            (row["unique_tcrs"], row["umi_sum"]),
            textcoords="offset points",
            xytext=(6, 3),
            fontsize=7,
            alpha=0.8,
        )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Unique TCRs (row count)")
    ax.set_ylabel("Total UMI count (sum of duplicate_count)")
    ax.set_title("Unique TCRs vs Total UMI counts (log-log)")
    ax.xaxis.set_major_formatter(ticker.LogFormatterSciNotation())
    ax.yaxis.set_major_formatter(ticker.LogFormatterSciNotation())
    plt.tight_layout()

    out_path = os.path.join(output_dir, "scatter_tcrs_vs_umi.png")
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {out_path}")


# ---------------------------------------------------------------------------
# Plot 3 – Per-file UMI cluster size histograms
# ---------------------------------------------------------------------------

def plot_umi_histograms(
    file_data: dict[str, pl.LazyFrame],
    output_dir: str,
) -> None:
    """Save one histogram per file showing av_UMI_cluster_size distribution."""
    col = "av_UMI_cluster_size"
    hist_dir = os.path.join(output_dir, "umi_histograms")
    os.makedirs(hist_dir, exist_ok=True)

    for name, lf in file_data.items():
        stem = Path(name).stem
        if col not in lf.collect_schema().names():
            print(
                f"Warning: '{col}' not found in '{name}', skipping histogram.",
                file=sys.stderr,
            )
            continue

        # Collect only the one column needed — third collect point
        values = (
            lf.select(pl.col(col).cast(pl.Float64, strict=False).drop_nulls())
              .collect()[col]
              .to_numpy()
        )

        if len(values) == 0:
            print(f"Warning: no valid values for '{col}' in '{name}', skipping.", file=sys.stderr)
            continue

        fig, ax = plt.subplots(figsize=(7, 4))
        sns.histplot(values, bins=40, kde=True, color="steelblue", ax=ax)
        ax.set_xlabel("av_UMI_cluster_size")
        ax.set_ylabel("Count")
        ax.set_title(f"UMI cluster size distribution\n{stem}")
        plt.tight_layout()

        out_path = os.path.join(hist_dir, f"{stem}_umi_hist.png")
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        print(f"Saved: {out_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyse immune repertoire gzipped TSV files and produce plots:\n"
            "  1. Pairwise Jaccard heatmap\n"
            "  2. Scatter: unique TCRs vs UMI counts\n"
            "  3. Per-file av_UMI_cluster_size histograms"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "patterns",
        nargs="+",
        metavar="PATTERN",
        help=(
            "Glob pattern(s) for input .tsv.gz files. "
            "Use ** for recursive matching, e.g. 'data/**/*.tsv.gz'."
        ),
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="tcr_plots",
        metavar="DIR",
        help="Directory where plots are saved (default: %(default)s).",
    )
    parser.add_argument(
        "--species-col",
        default="sequence",
        metavar="COLUMN",
        help=(
            "Column to use as the 'species' (set of unique values) for the "
            "Jaccard heatmap (default: %(default)s)."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Resolve files
    file_paths = resolve_files(args.patterns)
    if not file_paths:
        print("Error: no input files found. Check your glob patterns.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(file_paths)} file(s).")

    # Scan all files — no data read yet, just build lazy plans
    file_data: dict[str, pl.LazyFrame] = {}
    for path in file_paths:
        print(f"Scanning: {path}")
        try:
            lf = scan_file(path)
            file_data[path] = lf
            print(f"  → schema: {len(lf.collect_schema().names())} columns")
        except Exception as exc:
            print(f"  Error scanning '{path}': {exc}", file=sys.stderr)

    if not file_data:
        print("Error: no files loaded successfully.", file=sys.stderr)
        sys.exit(1)

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Plot 1 – Jaccard heatmap
    print("\nGenerating Jaccard heatmap…")
    plot_jaccard_heatmap(file_data, args.species_col, args.output_dir)

    # Plot 2 – Scatter
    print("Generating scatter plot…")
    plot_scatter(file_data, args.output_dir)

    # Plot 3 – UMI histograms
    print("Generating UMI cluster size histograms…")
    plot_umi_histograms(file_data, args.output_dir)

    print(f"\nDone. All plots saved to: {args.output_dir}/")


if __name__ == "__main__":
    main()
