#!/bin/bash
echo "Bash version ${BASH_VERSION}..."

# Description
  # recipe script to run Collapsinator for
  # all .n12.gz files in Decombinator repository

# How to run:
  # 1. from recipes folder:
    # ./Collapsinator.sh
    # or
    # source Collapsinator.sh

  # 2. from Decombinator-Tools folder:
    # ./recipes/Collapsinator.sh
    # or
    # source recipes/Collaspinsator.sh

  # 3. from Decombinator folder:
    # source /path/to/Decombinator-Tools/recipes/Collapsinator.sh

  # 4. Supplying path to Decombinator repository
    # source Collapsinator.sh /path/to/Decombinator

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

#running Collpasinator through loop
echo $0
chmod u+r+x ${toolsdir}/Collapsinator.sh
#for file in *.fq.gz
for file in $repo/*.n12.gz; do
  python ${repo}/Collapsinator.py -in $file &
done
wait
