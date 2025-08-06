# These are flags you must include - Two memory and one runtime.
# Runtime is either seconds or hours:min:sec
# 12hr selected to allow for instances of extended collapsing and server delay

#$ -l tmem=32G
#$ -l h_vmem=32G
#$ -l h_rt=24:00:00

# These are optional flags but you probably want them in all jobs

#$ -S /bin/bash
#$ -j y
#$ -N tcr_pipeline
#$ -cwd
#$ -l h=!arbuckle

# Most recent sequencing protocols return raw data that is already demultiplexed.
# Therefore, for most cases nowadays, running Demultiplexor is no longer required.

# Print useful troubleshooting information
hostname
date
echo $PWD

# Specify location of tags
PROJECTDIR=/SAN/colcc/tcr_decombinator
TAGS=$PROJECTDIR/Decombinator-Tags-FASTAs/

# Setup python enviroment
source /share/apps/source_files/python/python-3.11.9.source
source $PROJECTDIR/decombinator5_venv/bin/activate
python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'
echo "Decombinator version $(decombinator --version)"

# Get file name from directory and strip any directory information
FILENAME=$(find . -type f -name *_1.fq.gz -exec basename {} \;)
echo $FILENAME

# Delete the respective lines for alpha/beta if unneeded e.g. alpha has already
# run and this is a resubmission, or if running library with beta chain only
echo "Species assumed to be Homo sapiens, please specify if not"
echo "=== Alpha Chain Pipeline ==="
decombinator pipeline -in $FILENAME -br R2 -bl 22 -c a -ol TAKARA -tfdir $TAGS
echo "=== Beta Chain Pipeline ==="
decombinator pipeline -in $FILENAME -br R2 -bl 22 -c b -ol TAKARA -tfdir $TAGS

echo "Job complete."
