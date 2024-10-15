#!/usr/bin/env bash
# A script to generate a summary sheet from the current logs in the temp folder.

PROJECTDIR=/SAN/colcc/tcr_decombinator
TOOLS=$PROJECTDIR/Decombinator-Tools
TARGET_DIR=temp/

(return 0 2>/dev/null) && sourced=1 || sourced=0

read -epr "Please enter the pool ID: " POOLID

if [ -f "$POOLID" ]; then
    echo "$POOLID exists, proceeding with summarising."
else
    echo "$POOLID does not exist, please add it to the directory."
    echo 'Exiting.'
    if [ $sourced -eq 1 ]; then
        return
    else
        exit
    fi
fi

# Create temp directory for logs
echo "Creating temporary directory..."
mkdir temp_logs
DEST_DIR=temp_logs/

find $TARGET_DIR -type f -name "*.csv" | awk -v dest_dir="$DEST_DIR" -F'[_.]' '{
	n = split($0, parts, "/");
	filename = parts[n];
	split(filename, name_parts, "_");
	date = name_parts[1] "_" name_parts[2] "_" name_parts[3];
	numeric_date = name_parts[1] name_parts[2] name_parts[3];
	no_date_name = substr(filename, length(date) + 2);
	sub(/\.csv$/, "", filename);
	match(filename, /[0-9]*$/);

	if (RSTART > 0) {
		seq_num = substr(filename, RSTART);
		raw_id = substr(no_date_name, 1, RSTART - 1);
	} else {
		seq_num = 0;
		raw_id = no_date_name;
	}

	id = gensub(/_+$/, "", "g", raw_id);
	
	if (!seen[id] || numeric_date > seen_date[id] || (numeric_date == seen_date[id] && seq_num > seen_seq[id])) {
		seen_date[id] = numeric_date;
		seen_seq[id] = seq_num;
		files[id] = $0;
	}

} END {
	for (id in files) {
		print "Copying " files[id] " to " dest_dir;
		system("cp \"" files[id] "\" \"" dest_dir "\"");
	}
}'

# Generate summary sheet
echo "Creating temporary summary sheet..."
source /share/apps/source_files/python/python-3.11.9.source
current_time=$(date +"%Y-%m-%d_%H-%M-%S")
python3 $TOOLS/analysis/LogSummary.py -l temp_logs/ -o "Summary_${current_time}_${POOLID}" -s "$POOLID"

# Remove temp logs
echo "Removing temporary directory..."
rm -r temp_logs/

echo "Summary sheet generated."
