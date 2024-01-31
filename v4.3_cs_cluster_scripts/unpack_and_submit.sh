#!/bin/bash
# A script to be used alongside decombinator to automatically unpack RNAseq data from Novogene
# and submit for processing on the CS cluster 

# Record script start location
HOME=$(pwd)
# Untar tarball
TARNAME=$(find . -type f -name *.tar)
tar -xvf $TARNAME

DID=DualIndexDemultiplexed
# Change job based on human or mouse
JOB=dcr_job.qsub.sh

mkdir $DID

# Move all fastq files to directory
find . -type f -name *.gz -exec mv {} $DID/ \;

# Loop over fastq files and create folders per sample
for i in $DID/*
do
    # checks that i exists pre loop iteration
    [ -e "$i" ] || continue
    ID=${i%%_?.*}
    echo $ID
    # creates folder only if doesn't already exist e.g. X_2.fq
    # doesn't replace folder created by X_1.fq
    mkdir -p $ID
    mv $i $ID/
done

# Loop over sample directories, copy job in, submit job
for i in $DID/*
do
    [ -e "$i" ] || continue
    cp $JOB $i/
    cd $i/
    qsub $JOB
    cd $HOME
done