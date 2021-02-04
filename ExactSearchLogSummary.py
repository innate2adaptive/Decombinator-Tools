import os
import argparse

def args():
	parser = argparse.ArgumentParser(description='Generate qsub scripts for Decombinator pipeline')
	parser.add_argument('-in', '--indir', type=str, required=False, help='Main input directory, default: ExactSearchResults', default='ExactSearchResults')
	return parser.parse_args()

if __name__ == '__main__':
	args = args()

	outfile = args.indir + os.sep + "logSummary.csv"

	seqs = []
	summary = {}
	for r in os.listdir(args.indir):
		if not os.path.isdir(args.indir + os.sep + r):
			continue

		for f in os.listdir(args.indir + os.sep + r):
			
			if not f.endswith(".log"):
				continue			
			lines = open(args.indir + os.sep + r + os.sep + f, "r").readlines()
			in_file = os.path.basename(lines[0].rstrip().split(": ")[-1])
			line_count = lines[1].rstrip().split(": ")[-1]
			read_count = lines[2].rstrip().split(": ")[-1]
			av_read_len = lines[3].rstrip().split(": ")[-1]

			seq_counts_start = lines.index("counts:\n") + 1
			seq_counts = {}
			for l in lines[seq_counts_start:]:
				seq_id, seq_direction, seq, count = l.strip().split(", ")
				seq_counts[":".join([str(seq_id),seq_direction,seq])] = count

			summary[r] = {}
			summary[r]["file"] = in_file
			summary[r]["line_count"] = line_count
			summary[r]["read_count"] = read_count
			summary[r]["av_read_len"] = av_read_len
			summary[r]["counts"] = {}
			for s in seq_counts:
				summary[r]["counts"][s] = seq_counts[s]
				if not s in seqs:
					seqs.append(s)

	header = ", ".join(["file", "line count", "read count", "average read length"] + seqs)

	with open(outfile, "w") as ofile:
		ofile.write(header + "\n")
		for f in summary:
			row = [summary[f]["file"], summary[f]["line_count"], summary[f]["read_count"],
					 summary[f]["av_read_len"]]
			for seq in seqs:
				if seq in summary[f]["counts"]:
					row.append(summary[f]["counts"][seq])
				else:
					row.append("N/A")
			ofile.write(", ".join(row) + "\n")

	print("Including files:")
	for f in summary:
		print("\t"+summary[f]["file"])

	print("Summary saved to", outfile)



