#!/bin/bash
# A script to repack the directory structure created by `submit.sh`
# into the archival structures on the RDS in the raw and processed folders.
# Additionally requires a Sample Sheet with the desired odering of samples
# in the Summary Sheet.

PROJECTDIR=/SAN/colcc/tcr_decombinator
TOOLS=$PROJECTDIR/Decombinator-Tools

(return 0 2>/dev/null) && sourced=1 || sourced=0

read -p "How many .tsv files are you expecting?: " EXPECTED
ACTUAL=$(find temp/ -type f -name "*tsv*" | wc -l)

if [ $ACTUAL -eq $EXPECTED ]; then
    echo "Expected $EXPECTED .tsv files, found $ACTUAL .tsv files. Proceeding with repacking."
else
    echo "Expected $EXPECTED .tsv files, found $ACTUAL .tsv files. Verify this is correct and check the cshpc README for troubleshooting help."
    echo 'Exiting.'
    if [ $sourced -eq 1 ]; then
        return
    else
        exit
    fi 
fi

read -p "Please enter the pool ID: " POOLID

if [ -f $POOLID.csv ]; then
    echo "$POOLID.csv exists, proceeding with repacking. This will take 5 minutes..."
else
    echo "$POOLID.csv does not exist, please add it to the directory."
    echo 'Exiting.'
    if [ $sourced -eq 1 ]; then
        return
    else
        exit
    fi
fi

# RDS Raw directory structure
echo "Creating raw data storage directory..."
mkdir raw
mkdir raw/$POOLID
mkdir raw/$POOLID/DualIndexDemultiplexed
cp $POOLID.csv raw/$POOLID
find temp/ -type f -name "*.fq*" -exec cp {} raw/$POOLID/DualIndexDemultiplexed/ \;

# RDS Processed directory structure
echo "Creating processed data storage directory..."
mkdir processed
mkdir processed/$POOLID
mkdir processed/$POOLID/decombined
mkdir processed/$POOLID/collapsed
mkdir processed/$POOLID/translated
mkdir processed/$POOLID/logs

find temp/ -type f -name "*.n12*" -exec cp {} processed/$POOLID/decombined/ \;
find temp/ -type f -name "*.freq*" -exec cp {} processed/$POOLID/collapsed/ \;
find temp/ -type f -name "*.tsv*" -exec cp {} processed/$POOLID/translated/ \;
find temp/ -type f -name "*.csv*" -exec cp {} processed/$POOLID/logs/ \;

# Generate summary sheet
echo "Creating summary sheet..."
source /share/apps/source_files/python/python-3.10.0.source
python3 $TOOLS/analysis/LogSummary.py -l processed/$POOLID/logs/ -o processed/$POOLID/Summary_$POOLID.csv -s $POOLID.csv

echo "Repacking and summary complete. Please scp the files to the desired location."
echo "Take care not to overwrite any previous data that shares the name $POOLID!"
