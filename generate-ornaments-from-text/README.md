# generate-ornaments-from-text

## Overview

This is a simple set of scripts that generates 3D models from a set of objects described in text.

The basic pipeline is: text -> dalle3 -> dreamgaussian -> blender -> STL file

## 3D Models

![blender](blender_models.png)

## Images

<img src="images/belgian_malinois_dog.png" width="200">
<img src="images/BMW_supercar.png" width="200">
<img src="images/Mario_from_Super_Mario_Bros.png" width="200">
<img src="images/white_siamese_cat.png" width="200">
<img src="images/red_rose_with_stem.png" width="200">

## Usage

```bash
# Generate images to ./images
python3 get_images.py

# For each PNG, run the dreamgaussian pipeline against it
bash generate_3d_objects.sh
```