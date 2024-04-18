#!/bin/bash
# A script to repack the directory structure created by `unpack_and_submit.sh`
# into the archival structures on the RDS in the raw and processed folders.
# Additionally requires a Sample Sheet with the desired odering of samples
# in the Summary Sheet.

PROJECTDIR=/SAN/colcc/tcr_decombinator
TOOLS=$PROJECTDIR/Decombinator-Tools
read -p "Please enter the pool ID: " POOLID

if [ -f $POOLID.csv ]; then
    echo '$POOLID.csv exists, proceeding with repacking.'
else
    echo '$POOLID.csv does not exist, please add it to the directory.'
    exit
fi

# RDS Raw directory structure
mkdir raw
mkdir raw/$POOLID
mkdir raw/$POOLID/DualIndexDemultiplexed
cp $POOLID.csv raw/$POOLID
find temp/ -type f -name "*.fq*" -exec mv {} raw/$POOLID/DualIndexDemultiplexed/ \;

# RDS Processed directory structure
mkdir processed
mkdir processed/$POOLID
mkdir processed/$POOLID/decombined
mkdir processed/$POOLID/collapsed
mkdir processed/$POOLID/translated
mkdir processed/$POOLID/logs

find temp/ -type f -name "*.n12*" -exec mv {} processed/$POOLID/decombined/ \;
find temp/ -type f -name "*.freq*" -exec mv {} processed/$POOLID/collapsed/ \;
find temp/ -type f -name "*.tsv*" -exec mv {} processed/$POOLID/translated/ \;
find temp/ -type f -name "*.csv*" -exec mv {} processed/$POOLID/logs/ \;

# Generate summary sheet
source /share/apps/source_files/python/python-3.10.0.source
python3 $TOOLS/analysis/LogSummary.py -l processed/$POOLID/logs/ -o processed/$POOLID/Summary_$POOLID.csv -s $POOLID.csv

echo "Repacking and summary complete. Please scp the files to the desired location."
echo "Take care not to overwrite any previous data that shares the name $POOLID!"
