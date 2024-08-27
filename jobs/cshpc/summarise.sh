#!/bin/bash
# A script to generate a summary sheet from the current logs in the temp folder.

PROJECTDIR=/SAN/colcc/tcr_decombinator
TOOLS=$PROJECTDIR/Decombinator-Tools
TARGET_DIR=temp/

(return 0 2>/dev/null) && sourced=1 || sourced=0

read -p "Please enter the pool ID: " POOLID

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
DEST_DIR=temp_logs/

find $TARGET_DIR -type f -name "*.csv" | awk -v dest_dir="$DEST_DIR" -F'[_.]' '{
    date = $1 "_" $2 "_" $3;
    raw_id = substr($0, index($0, $4))
    if (!seen[raw_id] || date > seen[raw_id]) {
        seen[raw_id] = date;
        files[raw_id] = $0;
    }
} END {
    for (id in files) {
        print "Copying " files[id] " to " dest_dir;
        system("cp \"" files[id] "\" \"" dest_dir "\"");
    }
}'

# Generate summary sheet
echo "Creating temporary summary sheet..."
source /share/apps/source_files/python/python-3.11.9.source
current_time=$(date +"%Y-%m-%d_%H-%M-%S")
python3 $TOOLS/analysis/LogSummary.py -l temp_logs/ -o Summary_${POOLID}_${current_time}.csv -s $POOLID.csv

# Remove temp logs
echo "Removing temporary directory..."
rm -r temp_logs/

echo "Summary sheet generated."
