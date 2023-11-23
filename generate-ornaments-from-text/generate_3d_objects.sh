#!/usr/bin/env bash

function generate_3d_objects() {
    cd ~/dev/dreamgaussian
    source env/bin/activate
    filepath="$1"
    processed_filepath="${filepath/.png/_rgba.png}"
    base_filename=$(basename -- "$filepath")
    # get the parent directory of filepath
    parentname="$(dirname "$filepath")"



    echo "Processing $filepath"
    echo "Processed filepath: $processed_filepath"
    echo "Base filename: $base_filename"

    python3 process.py "$filepath" --size 512
    python3 main.py --config configs/image.yaml input=$processed_filepath save_path=$base_filename outdir=$parentname
    python3 main2.py --config configs/image.yaml input=$processed_filepath save_path=$base_filename outdir=$parentname
    cd -
}


# run generate_3d_objects against all files in images
# use absolute filepaths

for filepath in images/*.png; do
    # get absolute filepath
    filepath=$(realpath "$filepath")
    generate_3d_objects "$filepath"
done
