#!/bin/bash
# A script to repack the directory structure created by `unpack_and_submit.sh`
# into the archival structures on the RDS in the raw and processed folders.
# Additionally requires a Sample Sheet with the desired odering of samples
# in the Summary Sheet.

PROJECTDIR=/SAN/colcc/tcr_decombinator
TOOLS=$PROJECTDIR/Decombinator-Tools
read -p "Please enter the pool ID: " POOLID

# RDS Raw directory structure
mkdir raw
mkdir raw/$POOLID
cp $POOLID.csv raw/$POOLID
find temp/ -type f -name *.fq* -exec cp {} raw/$POOLID \;

# RDS Processed directory structure
mkdir processed
mkdir processed/$POOLID
mkdir processed/$POOLID/decombined/
mkdir processed/$POOLID/collapsed/
mkdir processed/$POOLID/translated
mkdir processed/$POOLID/logs

find temp/ -type f -name *.tsv* -exec mv {} processed/decombined/ \;
find temp/ -type f -name *.freq* -exec mv {} processed/collapsed/ \;
find temp/ -type f -name *.tsv* -exec mv {} processed/translated/ \;
find temp/ -type f -name *.csv* -exec mv {} processed/logs/ \;

# Generate summary sheet
python3 $TOOLS/LogSummary.py -l logs/ -o Summary_$POOLID.csv -s $POOLID.csv

echo "Repacking and summary complete. Please scp the files to the desired location."
echo "Take care not to overwrite any previous data that shares the name $POOLID!"
