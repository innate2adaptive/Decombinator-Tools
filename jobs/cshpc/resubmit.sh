#!/bin/bash

STARTDIR=$(pwd)
TEMPDIR=temp
# Rember to change job script based on species and protocol
JOB=dcr_job.qsub.sh

for i in $TEMPDIR/*
do
  cd $i/
  FILENAME=$(find . -type f -name "*.tsv*" -exec basename {} \;)
  if [ -z "${FILENAME}" ]
  then
    echo $i
    echo "No tsv found. Re-running with new job script."
    cp $STARTDIR/$JOB .
    qsub $JOB
  fi
  cd $STARTDIR
done

