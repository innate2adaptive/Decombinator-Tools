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
echo "$PWD"

# Specify location of tags
PROJECTDIR=/SAN/colcc/tcr_decombinator
TAGS=$PROJECTDIR/Decombinator-Tags-FASTAs/

# Setup python environment
source /share/apps/source_files/python/python-3.11.9.source
source $PROJECTDIR/decombinator5_venv/bin/activate
python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'
echo "Decombinator version $(decombinator --version)"

# Get file name from directory and strip any directory information
FILENAME=$(find . -type f -name "*_1.fq.gz" -exec basename {} \;)
echo "$FILENAME"

# Set up VSearch
export PATH=/share/apps/vsearch/bin:$PATH
source /share/apps/source_files/gcc-9.2.0.source
echo "Running VSearch"
vsearch --version

echo "Creating directory for logs..."
mkdir Logs
pattern="1.fq.gz"
replacement="2.fq.gz"
R2="${FILENAME/$pattern/$replacement}"
OUT=${FILENAME/$pattern/merge.fq}
if [[ -f "$R2" ]]; then
    echo "Merging $FILENAME with $R2"
    vsearch --fastq_mergepairs "${FILENAME}" \
        --reverse "$R2 "\
        --fastqout "$OUT "\
        --fastq_allowmergestagger \
        --log Logs/"${FILENAME/$pattern/merge.log}"
else
    echo "$R2, the paired read for $FILENAME could not be found."
    exit
fi

# For RACE: -br R2 -bl 42 -ol M13, for FUME: -br R1 -bl 22 -ol i8_single
# If running FUME, run vsearch on paired-end reads and submit merged fastq
# Delete the respective lines for alpha/beta if unneeded e.g. alpha has already
# run and this is a resubmission, or if running library with beta chain only
echo "Species assumed to be Homo sapiens, please specify if not"
echo "=== Beta Chain Pipeline ==="
decombinator pipeline -in "$OUT" -br R1 -bl 22 -c b -ol i8_single -tfdir "$TAGS"

# Zip merged file to save space now processing complete
gzip "$OUT"

echo "Job complete."
