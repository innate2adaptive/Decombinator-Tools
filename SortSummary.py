import os
import argparse

def args():
	parser = argparse.ArgumentParser(description='Sort Decombinator pipeline summary according to input list of samples')
	parser.add_argument('-s', '--summaryfile', type=str, help='Summary file to sort', required=True)
	parser.add_argument('-i', '--infile', type=str, help='File listing order of samples', required=True)
	return parser.parse_args()

args = args()

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

sorted_alpha_lines = []
sorted_beta_lines = []
sorted_other_lines = []

for s in samples:
	found_sample = False
	for summary in summary_data:
		line = summary_data[summary]
		if s in summary and 'alpha' in summary:
			if line not in sorted_alpha_lines:
				sorted_alpha_lines.append(line)
				found_sample = True

		elif s in summary and 'beta' in summary:
			if line not in sorted_beta_lines:
				sorted_beta_lines.append(line)
				found_sample = True

		elif s in summary:
			if line not in sorted_other_lines:
				sorted_other_lines.append(line)
				found_sample = True		

	if not found_sample:
		print("Warning: could not find sample containing", "'"+s+"'", "in", args.summaryfile)

sorted_output_lines = sorted_alpha_lines + sorted_beta_lines + sorted_other_lines

# check if all lines in summary are still in sorted summary
for summary in summary_data:
	line = summary_data[summary]
	if not line in sorted_output_lines:
		print("Warning:", summary, "in", args.summaryfile, "but no equivalent found in", args.infile)

new_summary_file = os.path.splitext(args.summaryfile)[0] + '.sorted.csv'

with open(new_summary_file, 'w') as outfile:
	outfile.write(header)
	for line in sorted_output_lines:
		outfile.write(line)

print("Sorted summary file saved to:", new_summary_file)

