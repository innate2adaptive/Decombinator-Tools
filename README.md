# Decombinator-Tools

This repository contains scripts that may be helpful when working with the [Decombinator](https://github.com/innate2adaptive/Decombinator) software.

## Navigation

- [Analysis](#analysis)
  - [Collapsed Sample Overlap](#collapsed-sample-overlap)
  - [Log Summary](#log-summary)
  - [Randomly Sample](#randomly-sample)
  - [TCR Repertoire Plots](#tcr-repertoire-plots)
  - [UMI Histogram](#umi-histogram)
- [Formatting](#formatting)
  - [DCR to Gene Name](#dcr-to-gene-name)
- [Generation](#generation)
  - [Test Data Generator](#test-data-generator)
- [Jobs](#jobs)
  - [Job Scripts](#job-scripts)
  - [Run Test Data](#run-test-data)

---

## Analysis

### Collapsed Sample Overlap

This script should be run using **R**.

The folder also contains examples of the plots produced by the script.

This script calculates the TCR overlap (using the 5-part Decombinator id, DCR) between any two samples produced using Collapsinator from Decombinator V4.

- The overlap is calculated as follows:
  Let A be the overlap matrix. Then for any two samples _i,j_,

  _A<sub>{i,j}</sub>_, the overlap with respect to row _i_, is

  > (Number of distinct DCRs found in both _i_ and _j_) / (number of unique DCRs in _i_).

- Note this is in general asymmetric (_A<sub>{i,j}</sub>_ is not equal to _A<sub>{j,i}</sub>_).

- The overlap matrix is then plotted as a heatmap, with red squares marking an overlap greater than (mean + 3 standard deviations). This threshold can be adjusted in the script.

- If comparing all samples in a particular sequencing run, note that as some runs contain several samples from the same individual/s,
  the absolute expected 'background' overlap will differ between runs.

- The script calculates and plots the overlap of the alpha files first followed by the beta.

---

### Log Summary

This script will generate a summary `.csv` file of all the data stored in the `Logs` folder within the Decombinator repository. This script is should be run in **Python 3**.

How to run:

```
python LogSummary.py -l /path/to/LogsFolder/ -o /path/to/outfile.csv
```

The output `.csv` file contains the following fields:

- **`sample`** — The sample name/identifier, derived from the log filename.
- **`NumberReadsInput`** — Total number of raw sequencing reads fed into the Decombinator pipeline.
- **`NumberReadsDecombined`** — Number of reads successfully assigned a TCR (T-cell receptor) rearrangement by Decombinator.
- **`PercentReadsDecombined`** — `NumberReadsDecombined / NumberReadsInput`. Fraction of input reads successfully decombined. Note: reported as a fraction despite the name.
- **`UniqueDCRsPassingFilters`** — Number of distinct DCR (Decombinator) identifiers (unique TCR rearrangements) remaining after quality/barcode filters.
- **`TotalDCRsPassingFilters`** — Total count of DCR reads passing filters, including duplicates (i.e. summed abundances across all unique DCRs).
- **`PercentDCRPassingFilters(withbarcode)`** — `TotalDCRsPassingFilters / NumberReadsDecombined`. Fraction of all decombined reads that pass filters with a barcode. Note: reported as a fraction despite the name.
- **`UniqueDCRsPostCollapsing`** — Number of distinct DCRs remaining after UMI/barcode collapsing (error correction and deduplication).
- **`TotalDCRsPostCollapsing`** — Total DCR count (with abundances) after collapsing.
- **`PercentUniqueDCRsKept`** — `UniqueDCRsPostCollapsing / UniqueDCRsPassingFilters`. Fraction of unique clonotypes retained through collapsing. Note: reported as a fraction despite the name.
- **`PercentTotalDCRsKept`** — `TotalDCRsPostCollapsing / TotalDCRsPassingFilters`. Fraction of total reads retained through collapsing. Note: reported as a fraction despite the name.
- **`AverageInputTCRAbundance`** — Mean number of reads per unique TCR clonotype before collapsing.
- **`AverageOutputTCRAbundance`** — Mean number of reads per unique TCR clonotype after collapsing.
- **`AverageRNAduplication`** — `TotalDCRsPassingFilters / TotalDCRsPostCollapsing`. Average RNA duplication level; how many pre-collapse reads correspond to each post-collapse DCR on average.

The order of the output summary will contain samples containing 'alpha' in their name, followed by those containing 'beta', followed by any additional samples that contain neither, all sorted alphabetically.

Alternatively, an additional argument can be used to specify the order of samples in the output summary file:

```
python LogSummary.py -l /path/to/LogsFolder/ -o /path/to/outfile.csv -s /path/to/order/of/samples.csv
```

The first column of this file should contain the sample names in the desired order, and the file should be comma-separated if it contains more than one column. This is designed to match the formatting of the index sample sheet used with Demultiplexor (which can simply be re-used here for the summary ordering).

---

### Randomly Sample

This script should be run using **Python 3**.

This script can be used to randomly sub-sample a file produced from the Decombinator pipeline (.fq, .n12, .freq, .cdr3, .np, .dcrcdr3) down to a specified sample size.

How to run:

```
python RandomlySample.py -in /path/to/infile.n12 -n 50
```

where the `-in` argument should be supplied with the file to be subsampled, and the `-n` argument should be supplied with the desired final sample size. The output file filename of the input file is prefixed by `subsampled_`. Note that the path will not be retained, and the output file will be written to the current working directory. Similarly, the Logs file will be stored in the current working directory.

To generate a subsampled file and Logs file in the Decombinator directory, run from within Decombinator:

```
python /path/to/Decombinator-Tools/RandomlySample.py -in infile.n12 -n 50
```

A full list of arguments can be viewed by running:

```
python RandomlySample.py -h
```

---

### TCR Repertoire Plots

This script should be run using **Python 3**.

This script reads one or more gzipped TSV files produced by the Decombinator pipeline and generates three plots summarising repertoire composition and sample overlap. Input files are expected to contain the standard Decombinator output columns including `sequence`, `duplicate_count`, and `av_UMI_cluster_size`.

#### Dependencies

Install the required packages before running:

```
pip install polars seaborn matplotlib numpy
```

#### How to run

```
python tcr_analysis.py PATTERN [PATTERN ...] [-o DIR] [--species-col COLUMN]
```

The positional `PATTERN` argument accepts standard shell glob syntax. Use `**` for recursive directory matching:

```
python tcr_analysis.py 'data/*.tsv.gz'
```

```
python tcr_analysis.py 'data/**/*.tsv.gz'
```

Multiple patterns can be supplied together:

```
python tcr_analysis.py 'cohort_a/**/*.tsv.gz' 'cohort_b/**/*.tsv.gz'
```

#### Output

Three plots are saved to the output directory (default: `tcr_plots/`):

| File                                 | Description                                                                  |
| ------------------------------------ | ---------------------------------------------------------------------------- |
| `jaccard_heatmap.png`                | Pairwise Jaccard index heatmap across all input files                        |
| `scatter_tcrs_vs_umi.png`            | Scatter plot of unique TCR count vs total UMI count per file (log-log scale) |
| `umi_histograms/<stem>_umi_hist.png` | Per-file histogram of `av_UMI_cluster_size` distribution                     |

The Jaccard heatmap compares sets of unique values in a chosen column across samples. The main diagonal is masked so that the colour scale reflects off-diagonal overlap only. The colorbar maximum is set dynamically to the highest observed pairwise overlap value.

#### Arguments

|    Argument     | Description                                                                                                                                                                                                                |
| :-------------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|    `PATTERN`    | One or more glob patterns for input `.tsv.gz` files. Quoted patterns with `**` will match recursively across subdirectories.                                                                                               |
|      `-o`       | Output directory for saved plots (default: `tcr_plots`). Created if it does not exist.                                                                                                                                     |
| `--species-col` | Column whose unique values are used as the set for Jaccard index calculation (default: `sequence`). Common alternatives include `junction_aa` for amino acid clonotype overlap or `decombinator_id` for DCR-level overlap. |

#### Examples

Plot all samples in a single directory, saving to `results/`:

```
python tcr_analysis.py 'samples/*.tsv.gz' -o results
```

Compare samples recursively across nested directories using junction amino acid sequences as the overlap unit:

```
python tcr_analysis.py 'study/**/*.tsv.gz' -o results --species-col junction_aa
```

A full list of arguments can be viewed by running:

```
python tcr_analysis.py -h
```

---

### UMI Histogram

This script should be run using **Python 3**.

This script can be used to generate a histogram plot displaying the frequency of average UMI cluster sizes present in collapsed TCR repertoire data. It should be run as an optional analysis tool in the Collapsinator stage of the Decombinator pipeline.

If Collapsinator has been run using the `-uh` argument, a `.csv` file will be saved to the logs folder with the suffix `_UMIhistogram.csv`. Supplying this file to the UMIHistogram script will generate the histogram.

How to run:

```
python UMIHistogram.py -in /path/to/filename_UMIhistogram.csv
```

The histogram plot will be saved to the same path as the input file. To change the output file, supply the `-o` argument:

```
python UMIHistogram.py -in /path/to/filename_UMIhistogram.csv -o /path/to/outfile.png
```

Additional arguments include `-b` to adjust the histogram bin size, `-c` to change the colour of the histogram (supply as text, e.g. `pink`, or as hexcode within quotes, e.g. `'#34623F'`), and `-d` to change the DPI of the output plot:

```
python UMIHistogram.py -in /path/to/filename_UMIhistogram.csv -b 80 -c '#34623F' -d 300
```

---

## Formatting

### DCR to Gene Name

This script should be run using **Python 3**.

The first five comma-delimited fields in a Decombinator or Collapsinator output file are referred to as the DCR identifier. The first two of these five fields are integer indices that correspond to V and J genes.

The `DCRtoGeneName` script reads in a file containing a DCR identifier and converts these first two V and J indices to the real gene name. The output (path and) file name is the same as the input name, but has prefixes the file extension with `tr_` e.g. `example.n12.gz` will convert to `example.tr_n12.gz`.

How to run:

```
python DCRtoGeneName.py -in path/to/input_alpha_file.n12.gz
```

If the chain name is not present in the input file name, it should be supplied by the user, e.g. :

```
python DCRtoGeneName.py -in path/to/input_file.freq -c beta
```

The default species for this script is assumed to be human, but can be changed with the `-sp` argument, e.g. `-sp mouse`. A full list of additional arguments can be viewed by running:

```
python DCRtoGeneName.py -h
```

---

## Generation

### Test Data Generator

The automatic test data generator can be used to produce customised FASTQ files to use as test input data for use with the [Decombinator Script](https://github.com/innate2adaptive/Decombinator#decombinator). This script should be run using **Python 3**.

Generic TCR alpha and beta chain FASTQ files for Decombinator can be generated by simply running:

```
python TestDataGenerator.py
```

Separate FASTQ files containing alpha and beta TCR sequences will be saved to a newly created `TestData` directory. Each file will contain 100 FASTQ reads each containing a V and J tag. The direction of these reads by default is in the reverse direction (which is also the default for Decombinator). By default, these sequences will include dummy barcodes (with a default barcode length of 42).

The id of each read in the FASTQ file contains information regarding which chain is present in the read, the direction of the read, whether the read contains one (SingleTag) or two (DualTag) tags, and a read-id.

#### Customisability

The test data generator can be provided a number of input arguments to customise the output test data. Information on these arguments can be found by running:

```
python TestDataGenerator.py -h
```

#### Input Arguments

| Argument | Description                                                                                                                                                                                                                                                             |
| :------: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|   `-d`   | change the name of the output directory for the test data                                                                                                                                                                                                               |
|  `-rl`   | change the read length of the output sequences (before barcoding)                                                                                                                                                                                                       |
|   `-n`   | change the total number of output reads per chain                                                                                                                                                                                                                       |
|   `-v`   | choose whether to produce dual tag or single tag output data                                                                                                                                                                                                            |
|  `-mc`   | produces a single output file of mixed alpha and beta chain TCRs                                                                                                                                                                                                        |
|  `-nbc`  | choose to produce non-barcoded data                                                                                                                                                                                                                                     |
|  `-bl`   | change the length of the attached barcode                                                                                                                                                                                                                               |
|  `-it`   | provide a percentage value for how many of the reads contain TCR sequences                                                                                                                                                                                              |
|  `-ie`   | provide a percentage value for how many tags contain one "sequencing" error                                                                                                                                                                                             |
|  `-mt`   | provide a percentage value for how many alpha and beta tags will have an overlapping match in single tag mode                                                                                                                                                           |
|  `-tf`   | direct the script to the local directory where tag files are stored. Useful for offline work. By default the script will first attempt to download the tags from the [Decombinator-Tags-FASTAs](https://github.com/innate2adaptive/Decombinator-Tags-FASTAs) directory. |
|  `-or`   | change the orientation of the output reads, 'reverse', 'forward', or 'both' (50% forward and 50% reverse)                                                                                                                                                               |
|  `-sp`   | change the species ('human' or 'mouse')                                                                                                                                                                                                                                 |
|  `-ol`   | change the oligo used ('i8' or 'm13')                                                                                                                                                                                                                                   |

#### Examples

- To create a file of 250 non-barcoded, mixed alpha and beta chain reads of 160 bp in length, stored in a directory called `MyData` run:

```
python TestDataGenerator.py -nbc -mc -n 250 -rl 160 -d MyData
```

- To create alpha and beta files for Single Tag Decombinator, in the forward direction, with 40% of sequences containing a sequencing error (1 bp substitution), run:

```
python TestDataGenerator.py -v s -or forward -ie 40
```

---

## Jobs

The run_scripts folder contains a number of bash scripts that can be used or modified as a shorthand to run over multiple input files in a directory.

---

### cshpc

_This guide is only relevant for members of the Innate2Adaptive group at UCL. At present it is designed to work with batches that have samples generated by a single protocol and species (e.g. RACE on Humans). If you are from another group utilising the COLCC resource, feel free to adapt the scripts found here. If you would like help with this, raise an issue in this repository and we will try to assist._

1. You will need access to the UCL CS HPC cluster which can be requested [here](https://hpc.cs.ucl.ac.uk/account-form/).
2. You will need to be added to the `inn2adap` user group to get access to our project storage. Ask for another member of the group to give you the directory path and request access for you when you obtain your login details.
   - In order to `cd` to the project storage you will need to directly `cd` to the project, due to dynamic mounting, the directory will not appear in `ls` or a directory GUI.
   - For convenience, create a bash script in your home directory with a `cd` command to the project directory.
3. Create a new batch directory in the project directory and place your `.tar` file there, make sure the `.tar` file is also backed up to the RDS as the project directory is not itself backed up.
   - See the UCL CS HPC [website](https://hpc.cs.ucl.ac.uk/ssh-scp/) for information on how to set up port-forwarding if you need to `scp` data to the cluster.
4. Copy the contents of `Decombinator-Tools/jobs/cshpc/` to your batch directory.
   - There are 6 scripts: `submit.sh` which you will call to unpack your `.tar` file and submit all of your samples as jobs, `dcr_job_XXXX.qsub.sh` is the job script which instructs the cluster how to treat your task - there is a variant for each library prep protocol that the lab uses (RACE and FUME), `resubmit.sh` is a handy script that you can use to resubmit any jobs which fail due to various reasons (see the troubleshooting section below), `summarise.sh` which can generate useful troubleshooting information from logs, and `repack.sh` which will format your processed data into the Chain lab standard storage format.
5. By default, `submit.sh` uses `dcr_job_race.qsub.sh`. Alter this if you are running FUME samples and check `dcr_job_XXXX.qsub.sh` to make sure it has the correct pipeline settings for your data.
   - If you have samples processed by different protocols in your batch, you will have to split them manually and edit `submit.sh` to skip the already completed steps.
6. Run `sh submit.sh` to submit all samples in the `.tar` file to the job scheduler.
7. Check if your jobs begin running successfully with `qstat`.
8. **TROUBLESHOOTING**: If a subset of jobs fails to complete, it may be due to memory or runtime limits. Investigate why using `summarise.sh` script. More detailed investigation can be performed using the `.o` files in each job subdirectory (feel free to ask for help with this). Edit the copy of `dcr_job_XXXX.qsub.sh` located in the top level of your batch directory, and then run `sh resubmit.sh`. This will resubmit all jobs that failed to complete, but using your new memory or runtime limits.
   - If your `.o` file ends with `MemoryError`, increase the memory requested in `dcr_job.qsub.sh`.
   - If your `.o` ends without any error message, the job likely hit the runtime limit. Increase the runtime requested in `dcr_job.qsub.sh`.
   - For other errors, inspect the error stack message carefully, as often it will be related to naming convention issues. Feel free to open an issue on this repository for help.
9. Create a `.csv` with your batch name and the order in which you would like your samples presented in the summary sheet.
10. To inspect qc metrics (as defined in `qc.py` in this repo), run `qc.sh`. By default this points at `temp/*/*.tsv.gz`, but the script will give you an opportunity to provide an alternate path.
11. Once all jobs are complete, check you have all the results you expected with `find temp/ -type f -name "*tsv*" | wc -l` (remove `| wc -l` to see filenames rather than counts), and then run `sh summarise.sh` to package the results for transfer to the RDS.
12. When you have verified that the data is safely saved onto the RDS, delete the batch directory containing the analysis on the CS HPC cluster. Only you have the permissions to delete this folder and we have a 500GB limit in the project directory.

---

### < V4.2 Additional scripts:

- [Decombinator.sh](#decombinator.sh)
- [Collapsinator.sh](#collapsinator.sh)

#### Decombinator.sh

This script will run Decombinator for all `.fq` and `.fq.gz` files in the Decombinator directory. Note that this script assumes the Decombinator and Decombinator-Tools repositories are located in the same parent directory. Otherwise, a path to the Decombinator repository should be supplied. Additionally, the `Logs` folder for these files will be located in the working directory from which the script is run - to keep log files in the Decombinator repository, follow step 4 below.

How to run:

1. from run_scripts folder:

```
./Decombinator.sh
```

or

```
source Decombinator.sh
```

2. from Decombinator-Tools folder:

```
./run_scripts/Decombinator.sh
```

or

```
source run_scripts/Collaspinsator.sh
```

3. from Decombinator folder:

```
source /path/to/Decombinator-Tools/run_scripts/Decombinator.sh
```

4. Supplying path to Decombinator repository

```
source Decombinator.sh /path/to/Decombinator
```

#### Collapsinator.sh

This script will run Collapsinator for all `.n12.gz` files in the Decombinator directory in parallel. Note that this script assumes the Decombinator and Decombinator-Tools repositories are located in the same parent directory. Otherwise, a path to the Decombinator repository should be supplied. Additionally, the `Logs` folder for these files will be located in the working directory from which the script is run - to keep log files in the Decombinator repository, follow step 4 below.

How to run:

1. from run_scripts folder:

```
./Collapsinator.sh
```

or

```
source Collapsinator.sh
```

2. from Decombinator-Tools folder:

```
./run_scripts/Collapsinator.sh
```

or

```
source run_scripts/Collaspinsator.sh
```

3. from Decombinator folder:

```
source /path/to/Decombinator-Tools/run_scripts/Collapsinator.sh
```

4. Supplying path to Decombinator repository

```
source Collapsinator.sh /path/to/Decombinator
```

---

### Job Scripts

The Job Scripts directory contains an example job script for running the [Decombinator Test Data](https://github.com/innate2adaptive/Decombinator-Test-Data) compatible with the University College London cluster setup. Some modifications may be required for other setups.

- You will need to install Decombinator-Tools in your local space on the cluster. After logging in, run the command:

  ```
  git clone https://github.com/innate2adaptive/Decombinator-Tools.git
  ```

- To use the job script, you must first have Decombinator and its required packages installed within a conda virtual environment in your local space on the cluster. Instructions are provided on the main [Decombinator README](https://github.com/innate2adaptive/Decombinator#running-decombinator-on-a-cluster).

- After Decombinator has been installed in your local space on the cluster, create an output directory for your data in your local Scratch space:
  ```
  mkdir Scratch/DCRExample
  ```
- Next, you will need to modify step 6 labelled in the job script `testdatajob.sh`, replacing `<user-id>` with your own user id. If you have named your output directory differently to `DCRExample`, this should also be changed in step 6. If you have named your conda environment differently from the example environment, this shop be changed in step 9 in the script.

- After making these changes, submit your job:
  ```
  qsub run_scripts/jobscripts/testdatajob.sh
  ```
- You can monitor your job using the `qstat` command. The initial state should show `qw` when waiting in the queue, and `r` when the job is running.
- The output of running the test data will be saved to `Scratch/DCRExample/files_from_job_<job_number>.tar.gz`. Extract your data, replacing `<job_number>` with your cluster job number, using:
  ```
  tar -xvzf Scratch/DCRExample/files_from_job_<job_number>.tar.gz
  ```

This template script can be modified and extended to run the Decombinator pipeline on any appropriate data.

---

### Run Test Data

This script should be run using **Python 3**.

This script can be used to automatically run the test data stored in the [Decombinator-Test-Data](https://github.com/innate2adaptive/Decombinator-Test-Data) repository through the Decombinator pipeline. The script assumes the directory structure shown below, where Decombinator, Decombinator-Tools, and Decombinator-Test-Data are stored in the same parent directory:

```
+-- parent-directory
|   +-- Decombinator
|   +-- Decombinator-Test-Data
|   +-- Decombinator-Tools
|   |   +-- RunTestData.py
```

How to run:

```
python RunTestData.py
```

Note that the output files and Log files will be stored in the current working directory (Decombinator-Tools). To generate output and Log files in the Decombinator directory, run from within Decombinator directory:

```
python /path/to/Decombinator-Tools/RunTestData.py
```

The RunTestData script can be supplied with two checkpoint arguments, `-c1` and `-c2` that tell the script at which part in the pipeline to start from and end at. For example, test data through only Demultiplexor and Decombinator, run:

```
python /path/to/Decombinator-Tools/RunTestData.py -c1 demultiplexor -c2 decombinator
```

or to run the test data through only Collapsinator, run:

```
python /path/to/Decombinator-Tools/RunTestData.py -c1 collapsinator -c2 collapsinator
```

---
