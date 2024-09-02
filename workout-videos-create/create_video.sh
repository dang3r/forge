#!/bin/bash

# Check if correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <csv_file> <video_title>"
    exit 1
fi

# Set variables
CSV_FILE="$1"
VIDEO_TITLE="$2"
OUTPUT_FILE="${VIDEO_TITLE}.mp4"

# Prepare the filter complex command
filter_complex=""
input_args=""

# Process each line in the CSV file
i=0
while IFS=',' read -r video_path video_description || [ -n "$video_path" ]; do
    # Remove leading/trailing whitespace
    video_path=$(echo "$video_path" | xargs)
    video_description=$(echo "$video_description" | xargs)
    echo "video_path: $video_path"
    echo "video_description: $video_description"
    
    input_args+=" -i $video_path"
    
    filter_complex+="[$i:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,"
    filter_complex+="drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:fontsize=32:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-tw)/2:y=h-th-50:text='$video_description'[v$i];"
    
    ((i++))
done < "$CSV_FILE"

# Concatenate the processed videos
for ((j=0; j<i; j++)); do
    filter_complex+="[v$j][$j:a]"
done
filter_complex+="concat=n=$i:v=1:a=1[outv][outa];"

# Add the title to the final video
filter_complex+="[outv]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:fontsize=48:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-tw)/2:y=50:text='$VIDEO_TITLE'[outv2]"

# Run ffmpeg command
ffmpeg $input_args -filter_complex "$filter_complex" -map "[outv2]" -map "[outa]" -c:v libx264 -c:a aac -shortest "${OUTPUT_FILE}"

echo "Video created: ${OUTPUT_FILE}"