#!/bin/bash

read -p "Enter the number of TSV files expected per folder: " EXPECTED_COUNT

STARTDIR=$(pwd)
TEMPDIR=temp
# Rember to change job script based on species and protocol
JOB=dcr_job.qsub.sh

for i in $TEMPDIR/*
do
  cd $i/
  # Count the number of TSV files in the folder
  TSV_COUNT=$(find . -type f -name "*.tsv*" | wc -l)
  
  if [ $TSV_COUNT -ne $EXPECTED_COUNT ]
  then
    echo $i
    echo "Expected $EXPECTED_COUNT TSV files, but found $TSV_COUNT. Re-running with new job script."
    cp $STARTDIR/$JOB .
    qsub $JOB
  fi
  
  cd $STARTDIR
done

