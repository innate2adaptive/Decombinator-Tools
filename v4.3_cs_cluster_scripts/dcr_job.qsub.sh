# These are flags you must include - Two memory and one runtime.
# Runtime is either seconds or hours:min:sec
# 12hr selected to allow for instances of extended collapsing and server delay

#$ -l tmem=15G
#$ -l h_vmem=15G
#$ -l h_rt=12:00:00

# These are optional flags but you probably want them in all jobs

#$ -S /bin/bash
#$ -j y
#$ -N tcr_pipeline
#$ -cwd

# Most recent sequencing protocols return raw data that is already demultiplexed.
# Therefore, for most cases nowadays, running Demultiplexor is no longer required.

# Print useful troubleshooting information
hostname
date
echo $PWD

# Setup python enviroment
source /share/apps/source_files/python/python-3.10.0.source
source ~/venvs/decombinator/bin/activate
python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'

# Specify locations of pipeline script and tags
PROJECTDIR=/SAN/colcc/tcr_decombinator
PIPELINE=$PROJECTDIR/Decombinator/dcr_pipeline.py
TAGS=$PROJECTDIR/Decombinator-Tags-FASTAs/

# Get file name from directory and strip any directory information
FILENAME=$(find . -type f -name *_1.fq.gz -exec basename {} \;)
echo $FILENAME

python $PIPELINE -fq $FILENAME -br R2 -bl 42 -c a -ol M13 -tfdir $TAGS
python $PIPELINE -fq $FILENAME -br R2 -bl 42 -c b -ol M13 -tfdir $TAGS

echo "Job complete."