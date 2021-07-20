# Written by Mazlina Ismail : July 2017
# Last updated by Thomas Peacock: August 2020 

#### Update Notes ####
  
  # update for Python 3
  # updated to run from Decombinator-Tools repository

##### Pseudocode #####

  # read in Decombinator log files
  # for each file
  # store Outputfile - this will be what we look for in the Coll log file
  # store the values we want from the Decombinator log file
  # read in Collapsing log files
  # find corresponding Outputfile name in the log file
  # store the values we want from the Collapsing log file

# output:
  # sample,NumberReadsInput,NumberReadsDecombined,PercentReadsDecombined,UniqueDCRsPassingFilters,TotalDCRsPassingFilters,PercentDCRPassingFilters(withbarcode),UniqueDCRsPostCollapsing,TotalDCRsPostCollapsing,PercentUniqueDCRsKept,PercentTotalDCRsKept,AverageInputTCRAbundance,AverageOutputTCRAbundance,AverageRNAduplication

# output comes from:
  # field 1 = Decombinator log, field 2-4 = Decombinator log, field 5-14 = Collapsing log

##### How to run #####

  # python LogSummary.py full/path/to/Logs/folder/ outfile.csv

# NB 
  # assumes that all Log files are in one Log folder
  # prints the output file to whatever directory you are in
  # may require slight modification on line 94, depending on character separator 
  # for grabbing filename in original log file

##### Py packages #####

from os import listdir, sep
from os.path import isfile, join
import sys
import argparse

def args():
  parser = argparse.ArgumentParser(description='Sort Decombinator pipeline summary according to input list of samples')
  parser.add_argument('-l', '--logpath', type=str, help='Full path to Logs folder', required=True)
  parser.add_argument('-o', '--outfile', type=str, help='Output log summary file', required=True)
  parser.add_argument('-s', '--sortfile', type=str, help='File listing order of samples for summary file', required=False) 
  return parser.parse_args()

##### Start #####
args = args()

pathToLogs = args.logpath # full path to Logs folder
outfile = args.outfile # output log summary file
summaryOrderFile = args.sortfile # optional file containing sample row order for summary file

# add slash to end of path if it is not supplied by user
if pathToLogs[-1] != "/":
  pathToLogs+="/"

onlyfiles = [f for f in listdir(pathToLogs) if isfile(join(pathToLogs, f))]

sampleNam = []

# get sample names from Decombinator log file
# then get values 
for f in onlyfiles:
    
    if 'Decombinator' in f:
        with open(pathToLogs+sep+f, 'r') as f:
            lines = f.read().splitlines()
            for l in lines:
                
                if 'OutputFile' in l:
                    spl = l.split(',')
                    sampleNam.append(spl[1])

fields = ["sample",
          "NumberReadsInput",
          "NumberReadsDecombined",
          "PercentReadsDecombined",
          "UniqueDCRsPassingFilters",
          "TotalDCRsPassingFilters",
          "PercentDCRPassingFilters(withbarcode)",
          "UniqueDCRsPostCollapsing",
          "TotalDCRsPostCollapsing",
          "PercentUniqueDCRsKept",
          "PercentTotalDCRsKept",
          "AverageInputTCRAbundance",
          "AverageOutputTCRAbundance",
          "AverageRNAduplication"]

out = {}

for i in sampleNam:

    # ignore undetermined files
    if "undetermined" in i.lower():
      continue

    string = [i]
    for j in onlyfiles:
        
        if 'Decombinator' in j:
            with open(pathToLogs+sep+j, 'r') as inf:
                lines = inf.read().splitlines()
                for idx, l in enumerate(lines):
                    
                    if 'OutputFile' in l:
                        nam = l.split(',')[1]
                        
                        if nam == i:
                            for item in lines[idx:]:
                                for patt in fields[1:4]:
                                    
                                    if patt in item:
                                        val = item.split(',')[1]
                                        string.append(val)

    for j in onlyfiles:
        
        if 'Collapsing' in j:
            with open(pathToLogs+j, 'r') as inf:
                lines = inf.read().splitlines()
                for idx, l in enumerate(lines):
                    
                    if 'InputFile' in l:
                        nam = l.split('/')[-1] # modify here for either
                                              # comma or slash
                        if nam == i:
                            for item in lines[idx:]:
                                for patt in fields[4:]:

                                    if patt in item:
                                        val = item.split(',')[1]
                                        string.append(val)

    # modify filename fun

    for char in ['.', '-']:
        if char in string[0]:
            string[0] = string[0].replace(char, '_')

    spl = string[0].split('_')[2:-2]

    a_idx = [i for i, x, in enumerate(spl) if x == 'a']
    b_idx = [i for i, x, in enumerate(spl) if x == 'b']

    # print(spl, a_idx, b_idx)

    if string[0].startswith('dcr_alpha'):

        for i, j in zip(a_idx, b_idx):

            if i < j:
                new_nam = 'alpha_' + '_'.join(spl[:i+1])
                string[0] = new_nam

            if i > j:
                new_nam = 'alpha_' + '_'.join(spl[j+1:])
                string[0] = new_nam

        if not b_idx:
            new_nam = 'alpha_' + '_'.join(spl)
            string[0] = new_nam

    if string[0].startswith('dcr_beta'):

        for i, j in zip(a_idx, b_idx):
            
            if i < j:
                new_nam = 'beta_' + '_'.join(spl[i+1:])
                string[0] = new_nam

            if i > j:
                new_nam = 'beta_' + '_'.join(spl[:j+1])
                string[0] = new_nam

        if not a_idx:
            new_nam = 'beta_' + '_'.join(spl)
            string[0] = new_nam
    
    outStr = ','.join(string)
    out[string[0]] = outStr

# get order from file (if supplied)
if summaryOrderFile:
  samples = []
  with open(summaryOrderFile, 'r') as samplefile:
    for line in samplefile:
      sample = line.rstrip().split(',')[0]
      # get correct names if unusual characters in name
      for char in ['.', '-']:
        if char in sample:
          sample = sample.replace(char, '_')
      samples.append(sample)

  sorted_output_lines = []
  # first sort by chain
  prefix = "dcr"
  suffix = "n12_gz"
  for chain in ['alpha', 'beta']:
    for s in samples:
      full_sample_name = "_".join([prefix, s, chain, suffix]) 

      if full_sample_name not in out:
       print("Warning: could not find", full_sample_name, "in Logs")
       continue  

      sorted_output_lines.append(out[full_sample_name])

# if no file provided, sort by chain and alphabetically
else:
  alpha_lines = []
  beta_lines = []
  other_lines = []
  # split into alpha and beta (or other)
  for sample, line in out.items():
    if 'alpha' in sample:
      alpha_lines.append(line)
    elif 'beta' in sample:
      beta_lines.append(line)
    else:
      other_lines.append(line)
  # sort alphabetically
  alpha_lines.sort()
  beta_lines.sort()
  other_lines.sort()
  # merge for full list
  sorted_output_lines = alpha_lines + beta_lines + other_lines

with open(outfile, 'w') as f:
    f.write(','.join(fields)+"\n")
    for string in sorted_output_lines:
        f.write("%s\n" % string)
