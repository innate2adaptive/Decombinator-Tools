import os
import sys
import urllib2
import argparse
import random
from Bio.Seq import Seq

def args():
	parser = argparse.ArgumentParser(description='Create Test Data For Use With Decombinator.py')
	parser.add_argument('-d', '--dir', type=str, help='Optional output directory name for test data', required=False, default='TestData')
	parser.add_argument('-rl', '--readlen', type=int, help='Length of read sequence (not including barcode)', required=False, default=100)
	parser.add_argument('-n', '--numreads', type=int, help='Number of reads to create per test file', required=False, default=100)
	parser.add_argument('-v', '--version', type =str, choices=['s','d','S','D'], help='Choose to produce Single tag or Dual tag data. (Use \'s\' or \'d\'.)', required=False, default='d')
	parser.add_argument('-mc', '--mixchains', action='store_true', help='Choose to produce data files with mixture of chains', required=False, default=False)
	parser.add_argument('-nbc', '--nonbarcoding', action='store_true', help='Create data without dummy barcoding', required=False, default=False)
	parser.add_argument('-bl', '--bclength', type=int, help='Length of dummy barcode, if applicable. Default is set to 42 bp.', required=False, default=42)
	parser.add_argument('-it', '--incltcr', type=int, help='Percentage of reads with tcrs', required=False, default=100)
	parser.add_argument('-ie', '--inclerr', type=int, help='Percentage of alpha and beta tags that contain 1 sequencing error', required=False, default=0)
	parser.add_argument('-mt', '--matchtags', type=int, help='Percentage of alpha and beta tags have an overlapping match (single tag mode)', required=False, default=100)
	parser.add_argument('-tf', '--tagfolder', type=str, help='Path to local directory where tags are stored for offline use', required=False, default='Decombinator-Tags-FASTAs')
	parser.add_argument('-or', '--orientation', type =str,help='Choose direction for reads (forward/reverse/both', required=False, default="reverse")
	return parser.parse_args()

def argCheck(args):
	taglength = 20 #hardcoded for now
	if args.version.lower() == 's' and args.readlen <= taglength:
		print "Single Tag version must have read length longer than",taglength
		sys.exit()
	if args.version.lower() == 'd' and args.readlen <= taglength*2:
		print "Dual Tag version must have read length longer than",taglength*2
		sys.exit()
	if not 0 <= args.incltcr <= 100:
		print "Reads with TCR percentage must be an integer between 0 and 100."
		sys.exit()
	if not 0 <= args.inclerr <= 100:
		print "Sequencing Error percentage must be an integer between 0 and 100."
		sys.exit()

def getTags(file,tagdir):
	fl = "https://raw.githubusercontent.com/innate2adaptive/Decombinator-Tags-FASTAs/master/" + file
	tags = []
	
	if os.path.isfile(file):
		with open(file) as f:
			lines = f.readlines()
		[tags.append(l.split(" ")[0]) for l in lines]

  	elif os.path.isfile(tagdir + os.sep + file):
		with open(tagdir + os.sep + file) as f:
			lines = f.readlines()
		[tags.append(l.split(" ")[0]) for l in lines]
	
	else:
		try:
			lines = urllib2.urlopen(fl).readlines()
			[tags.append(l.split(" ")[0]) for l in lines]
		except:
			print "Cannot find following file locally or online:", file
			print "Please either run with internet access, or point script to local copies of the tags with the \'-tf\' flag."
			sys.exit()

	return tags


def dataWriter(fname,data,directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

	with open(directory + os.sep + fname, "w") as f:
		for line in data:
			f.write(line+"\n")
	return

def randPartition(seqlen, partsize):
	# partitions seqlen into a vector of random numbers that sum to seqlen 
	partition = []
	total = 0

	for i in range(partsize - 1):
		if total >= seqlen:
			k = 0
		else:
			k = random.choice(range(seqlen-total))
		partition.append(k)
		total += k
	partition.append(max(0,seqlen - total))

	return partition

def buildSeq(readlen, v, j):
	bases = ['A','C','G','T']

	extrabases = readlen - len(v) - len(j)
	x, y, z = randPartition(extrabases, 3)

	xseq = "".join([random.choice(bases) for i in range(x)])
	yseq = "".join([random.choice(bases) for i in range(y)])
	zseq = "".join([random.choice(bases) for i in range(z)])	

	return [xseq + v + yseq + j + zseq]

def buildHalfSeqs(readlen, v, j, match = True):
	bases = ['A','C','G','T']

	extrabases = readlen - len(v)
	x, y = randPartition(extrabases, 2)

	xseq = "".join([random.choice(bases) for i in range(x)])
	yseq = "".join([random.choice(bases) for i in range(y)])

	if match == False:
		xfake = "".join([random.choice(bases) for i in range(x)])
		yfake = "".join([random.choice(bases) for i in range(y)])
		return (xseq + v + yseq, yfake + j + xfake)
	
	return (xseq + v + yseq, yseq + j + xseq)

def barcode(seq,bclen):
	#create dummy barcode for decombining purposes
	return "B"*bclen + seq

def buildRead(seq, readlen, chain, orientation, version, readid, seqid):
	read = "@Auto-Generated-Test-Data:"+chain+"chain:"
	if version == 'S':
		read += 'SingleTag:seq'+str(seqid)+":"
	elif version == 'D':
		read += 'DualTag:'
	read += orientation +":"
	read +="read-id-"+str(readid)+"\n"
	read += seq+"\n"
	read += "+\n"
	read += "~"*len(seq)  #dummy quality - '~' is highest FASTQ quality score
	return read

def createError(seq):
	bases = ['A','C','G','T']
	err = random.randint(0, len(seq)-1)
	bases.remove(seq[err])
	return seq[0:err] + random.choice(bases) + seq[err+1:]


def buildData(tags, readlen, numreads, orientation, version, nbc, bclen, inclerr, incltcr, matchtags):
	areads = []
	breads = []
	version = version.upper()
	bases = ['A','C','G','T']
	#start with dual tag
	for i in range(numreads):

		if incltcr > 0 and i >= (incltcr*numreads/100.0):
			newa = "".join([random.choice(bases) for j in range(readlen)])
			newb = "".join([random.choice(bases) for j in range(readlen)])
			if not nbc:
				newa = barcode(newa,bclen)
				newb = barcode(newb,bclen)
			ra = buildRead(newa ,readlen,"alpha",orientation,version,i,scount)
			rb = buildRead(newb ,readlen,"beta",orientation,version,i,scount)
			areads.append(ra)
			breads.append(rb)
			continue


		# select a random tag for each type and save to dictionary
		randtags = {tagtype: random.choice(t) for tagtype, t in tags.items()}

		if inclerr > 0 and i < (inclerr*numreads/100.0):
			asel = random.choice(['av','aj'])
			bsel = random.choice(['bv','bj'])

			randtags[asel] = createError(randtags[asel])
			randtags[bsel] = createError(randtags[bsel])

		if version == 'D':
			aseq = buildSeq(readlen, randtags['av'], randtags['aj'])
			bseq = buildSeq(readlen, randtags['bv'], randtags['bj'])
		elif version == 'S':
			if i >= (matchtags*numreads/100.0):
				aseq = buildHalfSeqs(readlen, randtags['av'], randtags['aj'], match=False)
				bseq = buildHalfSeqs(readlen, randtags['bv'], randtags['bj'], match=False)
			else:
				aseq = buildHalfSeqs(readlen, randtags['av'], randtags['aj'])
				bseq = buildHalfSeqs(readlen, randtags['bv'], randtags['bj'])

		if orientation.lower() == 'reverse':
			aseq = [str(Seq(s).reverse_complement()) for s in aseq]
			bseq = [str(Seq(s).reverse_complement()) for s in bseq]

		elif orientation.lower() == 'both' and i%2 == 0:
			aseq = [str(Seq(s).reverse_complement()) for s in aseq]
			bseq = [str(Seq(s).reverse_complement()) for s in bseq]

		if not nbc:
			aseq = [barcode(s,bclen) for s in aseq]
			bseq = [barcode(s,bclen) for s in bseq]

		scount = 1
		for s in aseq:
			read = buildRead(s,readlen,"alpha",orientation,version,i,scount)
			areads.append(read)
			scount += 1

		scount = 1
		for s in bseq:	
			read = buildRead(s,readlen,"beta",orientation,version,i,scount)
			breads.append(read)
			scount += 1

	return areads, breads


if __name__ == '__main__':

	args = args()
	argCheck(args)

	tag_files = {"aj" : "human_extended_TRAJ.tags",
				 "av" : "human_extended_TRAV.tags",
				 "bj" : "human_extended_TRBJ.tags",
				 "bv" : "human_extended_TRBV.tags"}

	tags = {}
	for t in tag_files:
		tags[t] = getTags(tag_files[t],args.tagfolder)

	prefix = args.version.lower()+"-"
	if args.nonbarcoding:
		prefix = "nbc-" + prefix

	if args.mixchains:
		data = buildData(tags, args.readlen, int(args.numreads/2), args.orientation, args.version, args.nonbarcoding, args.bclength, args.inclerr, args.incltcr, args.matchtags)
		outfiles = map(lambda f: prefix + f, ["alpha-beta-data.fq"])
		data = [data[0] + data[1]]

	else:
		data = buildData(tags, args.readlen, args.numreads, args.orientation, args.version, args.nonbarcoding, args.bclength, args.inclerr, args.incltcr, args.matchtags)
		outfiles = map(lambda f: prefix + f, ["alpha-data.fq", "beta-data.fq"])

	print "Data saved to:"
	for i in zip(outfiles, data):
		dataWriter(i[0], i[1], args.dir)
		print args.dir + os.sep + i[0]

