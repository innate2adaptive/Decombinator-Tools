#!/bin/bash
echo "Bash version ${BASH_VERSION}..."

# Description
  # recipe script to run Decombinator for
  # all .fq .fq.gz files in Decombinator repository
  # assumes default settings with chain name in fq file name

# How to run:
  # 1. from recipes folder:
    # ./Decombinator.sh
    # or
    # source Decombinator.sh

  # 2. from Decombinator-Tools folder:
    # ./recipes/Decombinator.sh
    # or
    # source recipes/Decombinator.sh

  # 3. from Decombinator folder:
    # source /path/to/Decombinator-Tools/recipes/Decombinator.sh

  # 4. Supplying path to Decombinator repository
    # source Decombinator.sh /path/to/Decombinator

# Check if Decombinator repository path is supplied,
# otherwise assume it exists on the same level as Decombinator-Tools
if [ -z "$1" ]; then
  wd=$(pwd)
  basedir=$(awk -F'Decombinator-Tools' '{print $1}' <<< ${wd})
  # if working directory is Decombinator directory
  if [[ $basedir == *'Decombinator' ]]; then
    repo=$basedir
  # otherwise assume Decombinator directory is in the base directory
  # i.e. the directory Decombinator-Tools sits in
  else	
    repo=${basedir}/Decombinator
  fi
else
  repo=$1
fi

toolsdir=${repo}-Tools

#running Decombinator though loop 
for file in ${repo}/*.fq*; do
  echo "Running ${file}..."
  python ${repo}/Decombinator.py -fq $file 
  echo ""
done
