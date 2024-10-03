#!/usr/bin/env bash
# A script to generate a summary sheet from the current logs in the temp folder.

PROJECTDIR=/SAN/colcc/tcr_decombinator
TOOLS=$PROJECTDIR/Decombinator-Tools

(return 0 2>/dev/null) && sourced=1 || sourced=0

read -ep "Please enter the pool ID: " POOLID

if [ -f $POOLID.csv ]; then
    echo "$POOLID.csv exists, proceeding with summarising."
else
    echo "$POOLID.csv does not exist, please add it to the directory."
    echo 'Exiting.'
    if [ $sourced -eq 1 ]; then
        return
    else
        exit
    fi
fi

# Create temp directory for logs
echo "Creating temporary directory..."
mkdir temp_logs

echo "Copying logs..."
find temp/ -type f -name "*.csv*" -exec cp {} temp_logs/ \;

# Generate summary sheet
echo "Creating temporary summary sheet..."
source /share/apps/source_files/python/python-3.10.0.source
current_time=$(date +"%Y-%m-%d_%H-%M-%S")
python3 $TOOLS/analysis/LogSummary.py -l temp_logs/ -o Summary_${POOLID}_${current_time}.csv -s $POOLID.csv

# Remove temp logs
echo "Removing temporary directory..."
rm -r temp_logs

echo "Summary sheet generated."
