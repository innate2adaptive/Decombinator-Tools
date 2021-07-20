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
	parser.add_argument('-r', '--rev', action='store_true', required=False, help='Set to also search fastq with reverse of subsequences')
	parser.add_argument('-c', '--comp', action='store_true', required=False, help='Set to also search fastq with complements of subsequences')	
	parser.add_argument('-rc', '--revcomp', action='store_true', required=False, help='Set to also search fastq with reverse complements of subsequences')
	parser.add_argument('-s', '--suppressout', action='store_true', required=False, help='Set to suppress output files and only write log file')
	return parser.parse_args()

def openerType(infile):
	if args.infile.endswith('.gz'):
		return gzip.open
	else:
		return open


def rev(s):
	return s[::-1]

def comp(s):
	return str(Seq(s).complement())

def revcomp(s):
	return str(Seq(s).reverse_complement())

def getSubseqs(subseqfile, reverse = False, complement = False, revcomplement = False):
	seqs = open(subseqfile, "r").readlines()
	seqs = {s.rstrip() : (i,"original") for i, s in enumerate(seqs)} # i to give id to original seqs
	extra_seqs = {}
	for s in seqs:
		if reverse:
			extra_seqs[rev(s)] = (seqs[s][0], "reverse") # preserve id of original seq
		if complement:
			extra_seqs[comp(s)] = (seqs[s][0], "complement")
		if revcomplement:
			extra_seqs[revcomp(s)] = (seqs[s][0], "revcomp")
	seqs.update(extra_seqs)
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

	matchdir = outdir + os.sep + os.path.basename(infile).split(".")[0] + "_matches"
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

	totalreadseqlen = 0
	opener = openerType(infile)
	start_time = time()
	print("Scanning...")
	with opener(infile, "rt") as ofile:
		for lcount, line in enumerate(ofile):
			if lcount % 4 == 0:
				read = [line.rstrip()]
			else:
				read.append(line.rstrip())
			if len(read) == 4:
				match = exactSearch(read, subseqs)
				totalreadseqlen += len(read[1])
				if match:
					if not suppressout:
						for r in read:
							openoutfiles[match].write(r+"\n")
					logs["counts"][match] += 1

			if (lcount+1) % 1000000 == 0:
				print("\t" + str(lcount+1) + " lines")

	scan_time = round(time() - start_time, 2)
	print("total of " + str(lcount+1) + " lines scanned")
	print("scan time: " + str(scan_time) + " seconds")
	logs["num_input_lines"] = lcount+1
	logs["num_input_reads"] = int((lcount+1)/4)
	logs["scan_time"] = scan_time
	logs["av_read_len"] = totalreadseqlen/((lcount+1)/4)
	for o in openoutfiles.values():
		o.close()

	outdir = os.path.dirname(outfiles[-1])
	writeLogs(logs, outdir)
	return 1

def listSubseqs(subseqs):
	list_format = []
	for s in subseqs:
		list_format.append((subseqs[s][0], subseqs[s][1], s))
	list_format.sort(key = lambda x: x[0])
	return list_format

def strSubseqs(list_subseqs):
	str_format = ""
	for s in list_subseqs:
		seq_string = " : ".join([str(s[0]), s[1], s[2]])
		str_format += "\n\t" + seq_string
	return str_format

def initLogs(args):
	logs = {}
	logs["infile"] = os.path.abspath(args.infile)
	logs["subseqfile"] =os.path.abspath(args.subseqfile)
	logs["rev"] = args.rev
	logs["comp"] = args.comp
	logs["revcomp"] = args.revcomp
	subseqs = getSubseqs(args.subseqfile, args.rev, args.comp, args.revcomp)
	list_subseqs = listSubseqs(subseqs)
	logs["list_subseqs"] =  list_subseqs
	logs["str_subseqs"] =  strSubseqs(list_subseqs)
	logs["counts"] = {s: 0 for s in subseqs}
	logs["num_input_lines"] = 0
	logs["num_input_reads"] = 0
	logs["av_read_len"] = 0
	logs["scan_time"] = 0
	return logs

def writeLogs(logs, outdir):
	outfile = outdir + os.sep + "summary.log"
	with open(outfile, "w") as ofile:
		ofile.write("infile: " + logs["infile"] + "\n")
		ofile.write("no. of input lines: " + str(logs["num_input_lines"]) + "\n")
		ofile.write("no. of input reads: " + str(logs["num_input_reads"])+ "\n")
		ofile.write("average read seq length: " + str(logs["av_read_len"])+ "\n")
		ofile.write("scan time: " + str(logs["scan_time"])+ "\n")
		ofile.write("subseqfile: " + logs["subseqfile"] + "\n")
		ofile.write("include rev: " + str(logs["rev"]) +"\n")
		ofile.write("include comp: " + str(logs["comp"]) +"\n")
		ofile.write("include revcomp: " + str(logs["revcomp"]) +"\n")
		ofile.write("subseqs: " + logs["str_subseqs"] +"\n")
		ofile.write("counts:" +"\n")
		for s in logs["list_subseqs"]:
		#	from IPython import embed
			c = ", ".join([ str(s[0]), s[1], s[2], str(logs["counts"][s[2]]) ])
			ofile.write("\t" + c + "\n")
		# for c in logs["counts"]:
		# 	ofile.write(c + ": " + str(logs["counts"][c]) + "\n")
	return 1

def exactSearch(read, subseqs):
	for s in subseqs:
		if s in read[1]:
			return s
	return None

if __name__ == '__main__':
	args = args()
	logs = initLogs(args)
	subseqs = getSubseqs(args.subseqfile, args.rev, args.comp, args.revcomp)
	print("Subsequences:")
	for s in subseqs:
		print("\t"+ " : ".join([s, str(subseqs[s][0]), subseqs[s][1]]))
	scanFastq(args.infile, list(subseqs.keys()), logs)




