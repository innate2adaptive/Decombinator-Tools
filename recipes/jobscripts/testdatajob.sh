#!/bin/bash -l
# 
# Script example to run Decombinator pipeline as serial job on Myriad (UCL)
# cluster using the Decombinator Test Data. More generic examples and
# instructions for running and monitoring jobs can be found at:
#    https://www.rc.ucl.ac.uk/docs/Example_Jobscripts/
# 
# NOTE: step 6 requires user-specific modification.
# 
# 1. Force bash as the executing shell.
#$ -S /bin/bash
# 2. Request 10 hours of wallclock time (format hours:minutes:seconds).
#$ -l h_rt=10:00:00
# 3. Request 1 gigabyte(s) of RAM
#$ -l mem=1G
# 4. Request 10 gigabyte(s) of TMPDIR space (default is 10 GB)
#$ -l tmpfs=10G
# 5. Set the name of the job.
#$ -N DCRExample
# 6. Set the working directory to somewhere in your scratch space.  This is
# a necessary step with the upgraded software stack as compute nodes cannot
# write to $HOME.
# NOTE: replace <user-id> with your own user id.
# NOTE: you must make sure the DCRExample directory exists before submitting
# this job script.
#$ -wd /home/<user-id>/Scratch/DCRExample
outdir=$(pwd)
echo $outdir
# 7. Your work *must* be done in $TMPDIR
cd $TMPDIR
# 8. Load python via miniconda module which provides access to your virtual
# environments
module load python/miniconda3/4.5.11
# 9. Activate your virtual environment. Make sure you have followed the
# instructions to create the environment first
source activate dcrpy3
# 10. Run the application. Here it assumed you are running the Decombinator
# test data stored in the Decombinator-Test-Data repository
# (https://github.com/innate2adaptive/Decombinator-Test-Data)

# set up some useful path variables:
dcrdir=$HOME/Decombinator
datadir=$HOME/Decombinator-Test-Data

# demultiplex data
python ${dcrdir}/Demultiplexor.py -r1 ${datadir}/R1.fastq.gz -r2 ${datadir}/R2.fastq.gz -i1 ${datadir}/I1.fastq.gz -ix ${datadir}/Indexes.ndx -dz

# Search the FASTQs produced for TCRs with Decombinator
 # Note that as the samples have their chains in the file name,
 # no chain designation is required
for f in *fq*; do echo $f; python ${dcrdir}/Decombinator.py -fq $f; done

# Error-correct the n12 files produced by Decombinator
 # Note that this test data set uses the I8 oligo
for f in *n12*; do echo $f; python ${dcrdir}/Collapsinator.py -in $f -ol I8; done

# Finally, translate the error-correct freq files and extract their CDR3s
for f in *freq*; do echo $f; python ${dcrdir}/CDR3translator.py -in $f; done

# Clean up tmp files (tag and fasta files from Decombinator-Tags-FASTAs
# repository) copied into TMPDIR
rm tmp*

# 11. Preferably, tar-up (archive) all output files onto the shared scratch area
tar zcvf ${outdir}/files_from_job_$JOB_ID.tar.gz $TMPDIR
# Make sure you have given enough time for the copy to complete!
