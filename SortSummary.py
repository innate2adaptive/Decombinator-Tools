import os
import argparse

def args():
	parser = argparse.ArgumentParser(description='Sort Decombinator pipeline summary according to input list of samples')
	parser.add_argument('-s', '--summaryfile', type=str, help='Summary file to sort', required=True)
	parser.add_argument('-i', '--infile', type=str, help='File listing order of samples', required=True)
	return parser.parse_args()

args = args()

prefix = "dcr"
suffix = "n12_gz"

header = None
summary_data = {}
with open(args.summaryfile, 'r') as sumfile:
	for i, line in enumerate(sumfile):
		if i == 0:
			header = line
			continue
		sample_name = line.rstrip().split(',')[0]
		summary_data[sample_name] = line

samples = []
with open(args.infile, 'r') as samplefile:
	for line in samplefile:
		sample = line.rstrip().split(',')[0]
		# borrow from original logSummary.py script
		for char in ['.', '-']:
			if char in sample:
				sample = sample.replace(char, '_')
		samples.append(sample)

sorted_output_lines = []
for chain in ['alpha', 'beta']:
	for s in samples:
		full_sample_name = "_".join([prefix, s, chain, suffix])

		if full_sample_name not in summary_data:
			print("Warning: could not find", full_sample_name, "in", args.summaryfile)
			continue

		sorted_output_lines.append(summary_data[full_sample_name])

new_summary_file = os.path.splitext(args.summaryfile)[0] + '.sorted.csv'

with open(new_summary_file, 'w') as outfile:
	outfile.write(header)
	for line in sorted_output_lines:
		outfile.write(line)

print("Sorted summary file saved to:", new_summary_file)

