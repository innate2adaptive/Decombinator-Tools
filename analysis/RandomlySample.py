# RandomlySample.py 
# March 2016, Jamie Heather, UCL
# Updated August 2020, Thomas Peacock, UCL
# Updated March 2024, Matthew Cowley, UCL

# Take a given file produced from the Decombinator pipeline (.fq, .n12, .freq, .cdr3) and randomly sub-sample to a given number

import time
import argparse
import gzip
import collections as coll
import re
import random
import sys, os

def args():
    """args(): Obtains command line arguments which dictate the script's behaviour"""

    # Help flag
    parser = argparse.ArgumentParser(
        description='Script to randomly subsample output files produced throughout the Decombinator pipeline to a fixed number')
    # Add arguments
    parser.add_argument(
        '-in', '--infile', type=str, help='infile', required=True)
    parser.add_argument(
        '-ft', '--filetype', type=str, help='File type, if not given in filename (fq/n12/cdr3/np/dcrcdr3/). \"line\" just randomly selects lines from infile.', required=False)
    parser.add_argument(
        '-n', '--number', type=int, help='Number of lines/reads to subsample to.', required=True)  
    parser.add_argument(
        '-s', '--suppresssummary', action='store_true', help='Output summary data (True/False)', required=False)
    parser.add_argument(
        '-dz', '--dontgzip', action='store_true', help='Stop the output files automatically being compressed with gzip (True/False)', required=False)
    parser.add_argument(
        '-pf', '--prefix', type=str, help='Specify the filename prefix of the output files. Default = \"subsampled_\"', required=False, default='subsampled_')
    
    return parser.parse_args()

def find_symbol_positions(line, symbol):
    """ Return the location of all the commas in an input string or line """
    return [m.start() for m in re.finditer(symbol, line)] 

def get_file_type(infile, opener):
    """ Determine the input file type (.fq, .n12, .freq, .cdr3, .np, .dcrcdr3, dcr) """
    with opener(infile, "rt") as fl:
      test_lines = [next(fl) for x in range(4)]    

    file_type = ""
    comma = find_symbol_positions(test_lines[0], ',')
    tab = find_symbol_positions(test_lines[0], "\t")
    
    if test_lines[0][0] == "@" and test_lines[2][0] == "+" and len(test_lines[1]) == len(test_lines[3]):
      file_type = 'fq'

    elif ':' in test_lines[0] and len(comma) == 5:
      if '_' in test_lines[0]:
        file_type = 'np'
      else:
        file_type = 'dcrcdr3'
        
    else:
      if len(comma) == 0 and len(tab) > 0:
        file_type = 'cdr3'
      elif len(comma) == 6:
        file_type = 'freq'  
      elif len(comma) == 9 or len(comma) == 0:
        file_type = 'n12'  
      elif len(comma) == 4:
        file_type = 'dcr'

    if file_type:
      return file_type
    else:
      print("Unable to determine file type.")
      sys.exit()
  
def readfq(fp): 
    """
    readfq(file):Heng Li's Python implementation of his readfq function 
    https://github.com/lh3/readfq/blob/master/readfq.py
    """
    
    last = None # this is a buffer keeping the last unprocessed line
    while True: # mimic closure; is it a bad idea?
        if not last: # the first record or a record following a fastq
            for l in fp: # search for the start of the next record
                if l[0] in '>@': # fasta/q header line
                    last = l[:-1] # save this line
                    break
        if not last: break
        name, seqs, last = last[1:].partition(" ")[0], [], None
        for l in fp: # read the sequence
            if l[0] in '@+>':
                last = l[:-1]
                break
            seqs.append(l[:-1])
        if not last or last[0] != '+': # this is a fasta record
            yield name, ''.join(seqs), None # yield a fasta record
            if not last: break
        else: # this is a fastq record
            seq, leng, seqs = ''.join(seqs), 0, []
            for l in fp: # read the quality
                seqs.append(l[:-1])
                leng += len(l) - 1
                if leng >= len(seq): # have read enough quality
                    last = None
                    yield name, seq, ''.join(seqs); # yield a fastq record
                    break
            if last: # reach EOF before reading enough quality
                yield name, seq, None # yield a fasta record instead
                break

def sort_permissions(fl):
    # Need to ensure proper file permissions on output data
      # If users are running pipeline through Docker might otherwise require root access
    if oct(os.stat(fl).st_mode)[4:] != '666':
      os.chmod(fl, 0o666)

if __name__ == '__main__':

    inputargs = vars(args())
    counts = coll.Counter()
    
    counts['start_time'] = time.time()

    inbasefile = os.path.basename(inputargs['infile'])
    inbasepath = os.path.dirname(inputargs['infile'])

    # Set file openers
    if inputargs['infile'].endswith('.gz'):
      in_opener = gzip.open
    else:
      in_opener = open
    
    if inputargs['dontgzip'] == True:
      out_opener = open
      outfilename = inputargs['prefix'] + inbasefile
      if outfilename.endswith('.gz'):
        outfilename = outfilename[:-3]
    else:
      out_opener = gzip.open
      if inputargs['infile'].endswith('.gz'):
        outfilename = inputargs['prefix'] + inbasefile
      else:
        outfilename = inputargs['prefix'] + inbasefile + '.gz'

      if not inbasepath=="":
        outfilename = os.sep.join([inbasepath, outfilename])
    
    # Test whether infile present
      # FIX
    
    # Find file type
    if inputargs['filetype']:
      file_type = inputargs['filetype']
    else:
      file_type = get_file_type(inputargs['infile'], in_opener)
    
    if file_type in ['dcrdcr3', 'np', 'line']:
       print(f"Support for .{file_type} has been depreciated. Please use an earlier version of this script if support is required.")
       sys.exit()

    if file_type not in ['fq', 'n12', 'cdr3', 'freq', 'dcr']:
      print("File type not recognised. Please include in file name or set -ft flag appropriately.")
      sys.exit() 

    if file_type in ['n12', 'dcr', 'fq']: # File types that are in no way collapsed
      with_frequency = False
      print(f"Reading .{file_type} without frequency information.")
    else:
      with_frequency = True
      print(f"Reading .{file_type} with frequency information.")
      
    whole_list = []
        
    # Open infile, determine type, read into list and sample
      # fq, misc dcr files and n12 files are not collapsed, in that they contain no frequency information (every line is a unique entry)
      # Everything that has been collapsed (freq, cdr3, np, dcrcdr3) has a final comma-delimited frequency file, therefore need to be weighted accordingly
    with in_opener(inputargs['infile'],"rt") as infile, out_opener(outfilename, 'wt') as outfile:
      
      print("Reading in data from", inputargs['infile'])
      
      if file_type == 'fq':
        for readid, seq, qual in readfq(infile):
          whole_list.append([readid, seq, qual])
          counts['in_count'] += 1
        
      else:
        if file_type == "freq":
           freq_index = -2
           symbol = ","
        elif file_type == "cdr3":
           freq_index = 4
           symbol = "\t"

        for line in infile:
          if file_type == "cdr3" and counts['in_lines'] == 0:
             cdr3_header = line
             counts['in_lines'] += 1
             continue
          counts['in_lines'] += 1
          
          if with_frequency == False:
            counts['in_count'] += 1
            whole_list.append(line.rstrip())
          
          else:
            symbol_positions = find_symbol_positions(line, symbol)
            if file_type == "freq":
              identifier = line
              freq = int(re.sub('[, ]', '', line[symbol_positions[freq_index]:symbol_positions[freq_index + 1]]))
            elif file_type == "cdr3":
              identifier = line
              freq = int(re.sub('[\t ]', '', line[symbol_positions[freq_index]:symbol_positions[freq_index + 1]]))
            counts['in_count'] += freq
            
            for i in range(freq):
              whole_list.append(identifier)
      
      if inputargs['number'] > counts['in_count']:
        print("Cannot sub-sample to " + "{:,}".format(inputargs['number']) +": greater than number of input lines/reads (" + "{:,}".format(counts['in_count']) + ").")
        sys.exit()
      else:
        print("{:,}".format(counts['in_count']), "input lines/reads: sampling to", "{:,}".format(inputargs['number']))
      
      sampled = random.sample(whole_list, inputargs['number'])
      
      print("Writing subsampled lines/reads to", outfilename)
      if with_frequency == True:
        collapsed = coll.Counter()
        for s in sampled:
          collapsed[s] += 1
        
        for c in collapsed.most_common():
          if file_type == "cdr3":
            if counts["header_added"] == 0:
               outfile.write(cdr3_header)
               counts["header_added"] += 1
            list_c = c[0].split("\t")
            list_c[5] = " " + str(c[1])
            outline = "\t".join(list_c)
            outfile.write(outline)
          else:
            list_c = c[0].split(",")
            list_c[-2] = " " + str(c[1])
            outline = ",".join([str(i) for i in list_c])
            outfile.write(outline)
        
        counts['number_unique_outlines'] = len(collapsed)
      
      elif with_frequency == False:
        for s in sampled:
          if file_type == 'fq':
            outline = '@' + s[0] + '\n' + s[1] + '\n+\n' + s[2] + '\n' 
          else:
            outline = s + '\n'
          outfile.write(outline)

    sort_permissions(outfilename)
    
    counts['end_time'] = time.time()
    
    # Write data to summary file
    if inputargs['suppresssummary'] == False:
    
      # Check for directory and make summary file
      if not os.path.exists('Logs'):
        os.makedirs('Logs')
      date = time.strftime("%Y_%m_%d")
      
      # Check for existing date-stamped file
      samplenam = inbasefile.split(".")[0]
      summaryname = "Logs/" + date + "_" + samplenam + "_Subsampling_Summary.csv"
      if not os.path.exists(summaryname): 
        summaryfile = open(summaryname, "wt")
      else:
        # If one exists, start an incremental day stamp
        for i in range(2,10000):
          summaryname = "Logs/" + date + "_" + samplenam + "_Subsampling_Summary" + str(i) + ".csv"
          if not os.path.exists(summaryname): 
            summaryfile = open(summaryname, "wt")
            break
          
      # Generate string to write to summary file 
      summstr = "Property,Value\nDirectory," + os.getcwd() + "\nInputFile," + inputargs['infile'] + "\nOutputFile," + outfilename \
        + "\nDateFinished," + date + "\nTimeFinished," + time.strftime("%H:%M:%S") + "\nTimeTaken(Seconds)," \
        + str(round((counts['end_time']-counts['start_time']),2)) + "\n\nInputArguments:,\n"
      
      for s in ['filetype','prefix', 'dontgzip', 'number']:
        summstr = summstr + s + "," + str(inputargs[s]) + "\n"
        
      summstr = summstr + "\nNumberUniqueLinesReadIn," + str(counts['in_lines']) 
      
      if with_frequency == True:
        summstr = summstr + "\nNumberTotalIdentifiersReadIn," + str(counts['in_count']) \
          + "\nNumberUniqueIdentifiersOutput," + str(counts['number_unique_outlines']) 
      
      print(summstr, file=summaryfile)
      summaryfile.close()
      sort_permissions(outfilename)

    sys.exit()