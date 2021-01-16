"""
Script to perform search of exact subsequences in Fastq data
"""
import os
import gzip
import argparse
from Bio.Seq import Seq
from time import time

def args():
	parser = argparse.ArgumentParser(description='Generate qsub scripts for Decombinator pipeline')
	parser.add_argument('-in', '--infile', type=str, required=True, help='Input fastq or fastq.gz file to scan')
	parser.add_argument('-sf', '--subseqfile', type=str, required=True, help='File listing subsequences to search for in fastq reads')
	parser.add_argument('-rc', '--revcomp', action='store_true', required=False, help='Set to also search fastq with reverse complements of subsequences')
	parser.add_argument('-s', '--suppressout', action='store_true', required=False, help='Set to suppress output files and only write log file')
	return parser.parse_args()

def openerType(infile):
	if args.infile.endswith('.gz'):
		return gzip.open
	else:
		return open

def revcomp(s):
	return str(Seq(s).reverse_complement())

def getSubseqs(subseqfile, rc = False):
	seqs = open(subseqfile, "r").readlines()
	seqs = [s.rstrip() for s in seqs]
	if rc:
		rc_seqs = [revcomp(s) for s in seqs]
		seqs += rc_seqs
	return seqs

def createOutfiles(infile, subseqs, outdir="ExactSearchResults"):
	outfiles = []
	if not os.path.isdir(outdir):
		os.mkdir(outdir)

	# if os.path.isdir(outdir):
	# 	k = 1
	# 	while os.path.isdir(outdir+str(k)):
	# 		k +=1
	# 	outdir = outdir + str(k)
	# os.mkdir(outdir)

	matchdir = outdir + os.sep + infile.split(".")[0] + "_matches"
	os.mkdir(matchdir)
	for s in subseqs:
		f = matchdir + os.sep + s + ".fastq"
		open(f, "w").close()
		outfiles.append(f)
	return outfiles


def scanFastq(infile, subseqs, logs, suppressout = False):
	if not suppressout:
		outfiles = createOutfiles(infile, subseqs)
		openoutfiles = {os.path.basename(ofile).split(".")[0] : open(ofile, "w") for ofile in outfiles}

	opener = openerType(infile)
	start_time = time()
	print("Scanning...")
	with opener(infile, "r") as ofile:
		for lcount, line in enumerate(ofile):
			if lcount % 4 == 0:
				read = [line.rstrip()]
			read.append(line.rstrip())
			match = exactSearch(read, subseqs)
			if match:
				if not suppressout:
					for r in read:
						openoutfiles[match].write(r+"\n")
				logs[match] += 1
			if lcount+1 % 1000000 == 0:
				print("\t" + str(lcount) + " lines")

	scan_time = round(time() - start_time, 2)
	print("total of " + str(lcount+1) + " lines scanned")
	print("scan time: " + str(scan_time) + " seconds")
	logs["num_input_lines"] = lcount+1
	logs["num_input_reads"] = (lcount+1)/4
	logs["scan_time"] = scan_time
	for o in openoutfiles.values():
		o.close()

	outdir = os.path.dirname(outfiles[-1])
	writeLogs(logs, outdir)
	return 1

def initLogs(args):
	logs = {}
	logs["infile"] = os.path.abspath(args.infile)
	logs["subseqfile"] =os.path.abspath(args.subseqfile)
	logs["revcomp"] = args.revcomp
	subseqs = getSubseqs(args.subseqfile, args.revcomp)
	logs["subseqs"] =  ", ".join(subseqs)
	logs["counts"] = {s: 0 for s in subseqs}
	logs["num_input_lines"] = 0
	logs["num_input_reads"] = 0
	logs["scan_time"] = 0
	return logs

def writeLogs(logs, outdir):
	outfile = outdir + os.sep + "summary.log"
	with open(outfile, "w") as ofile:
		ofile.write("infile: " + logs["infile"] + "\n")
		ofile.write("no. of input lines: " + str(logs["num_input_lines"]) + "\n")
		ofile.write("no. of input reads: " + str(logs["num_input_reads"])+ "\n")
		ofile.write("scan time: " + str(logs["scan_time"])+ "\n")
		ofile.write("subseqfile: " + logs["subseqfile"] + "\n")
		ofile.write("include revcomp: " + str(logs["revcomp"]) +"\n")
		ofile.write("subseqs: " + logs["subseqs"] + "\n")
		for c in logs["counts"]:
			ofile.write(c + ": " + str(logs["counts"][c]) + "\n")
	return 1

def exactSearch(read, subseqs):
	for s in subseqs:
		if s in read:
			return s
	return None

if __name__ == '__main__':
	args = args()
	logs = initLogs(args)
	subseqs = getSubseqs(args.subseqfile, args.revcomp)
	print("Subsequences:")
	for s in subseqs:
		print("\t"+s)
	scanFastq(args.infile, subseqs, logs)




