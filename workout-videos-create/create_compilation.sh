#!/bin/bash

set -e


# Create a temporary directory to store processed videos
TEMP_DIR="./temp_videos"
mkdir -p "$TEMP_DIR"

# Process each input filename from the file
while IFS= read -r filename; do
    echo "Processing: '$filename'"

    base_name=$(basename "$filename")
    name_no_ext="${base_name%.*}"
    output_temp="$TEMP_DIR/$base_name"

    ffmpeg -nostdin -i "$filename" \
        -vf "drawtext=text='$name_no_ext':\
fontcolor=white:\
fontsize=72:\
box=1:\
boxcolor=black@0.5:\
boxborderw=5:\
x=(w-text_w)/2:\
y=h-th-10,\
scale=iw/3:-2" \
        -c:v libx265 \
        -crf 30 \
        -preset veryfast \
        -c:a copy \
        "$output_temp"
done

# Concatenate all processed videos
cd "$TEMP_DIR"
echo "Concatenating videos..."
find . -name '*.mp4' | sort | xargs -I {} echo "file '{}'" > concat_list.txt
ffmpeg -nostdin -f concat -safe 0 -i "concat_list.txt" -c:v libx265 -crf 23 -preset medium -c:a copy "../output_concatenated.mp4"
cd ..

rm -rf "$TEMP_DIR"

echo "Done! Final video saved as output_concatenated.mp4"
