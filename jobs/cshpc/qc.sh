#!/usr/bin/env bash
# A script to produce QC plots for decombinator runs.
# See qc.py for details.
PROJECTDIR=/SAN/colcc/tcr_decombinator
TOOLS=$PROJECTDIR/Decombinator-Tools
source /share/apps/source_files/python/python-3.11.9.source
source $PROJECTDIR/decombinator_qc_venv/bin/activate

read -p "Please enter the glob path to the .tsv files to be qc'd: " TSV_GLOB

python3 $TOOLS/analysis/qc.py $TSV_GLOB -o qc_plots
