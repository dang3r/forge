#!/usr/bin/env bash

IMAGE_DIRECTORY="$1"
OUTPUT_DIRECTORY="$2"
if [ -z "$IMAGE_DIRECTORY"  || -z "$OUTPUT_DIRECTORY"]
then
    echo "No image directory or output directory specified"
    exit 1
fi

IMAGE_DIRECTORY=$(realpath "$IMAGE_DIRECTORY")
OUTPUT_DIRECTORY=$(realpath "$OUTPUT_DIRECTORY")

function generate_3d_objects() {
    cd ~/dev/dreamgaussian
    source env/bin/activate
    filepath="$1"
    processed_filepath="${filepath/.png/_rgba.png}"
    processed_filepath="$OUTPUT_DIRECTORY/$(basename -- "$processed_filepath")"
    tmp_filepath="$OUTPUT_DIRECTORY/$(basename -- "$filepath")"
    base_filename=$(basename -- "$filepath")


    cp "$filepath" $OUTPUT_DIRECTORY

    echo "Processing $filepath"
    echo "Processed filepath: $processed_filepath"
    echo "Base filename: $base_filename"

    python3 process.py "$tmp_filepath" --size 512
    python3 main.py --config configs/image.yaml input=$processed_filepath save_path=$base_filename outdir=$OUTPUT_DIRECTORY
    python3 main2.py --config configs/image.yaml input=$processed_filepath save_path=$base_filename outdir=$OUTPUT_DIRECTORY
    cd -
}


for filepath in $IMAGE_DIRECTORY/*png; do
    filepath=$(realpath "$filepath")
    generate_3d_objects "$filepath"
done
