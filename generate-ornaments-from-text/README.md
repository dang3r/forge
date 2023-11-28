# generate-ornaments-from-text

## Overview

Its almost Christmas time and I wanted to make see if any of the recent AI developments could help gifts. After learning
about dreamgaussian, I thought it would be fun to generate ornaments for the christmas tree.

This project glues together dreamgaussian, dalle3 (or other text to image models), and blender to generate 3D models.

The basic pipeline is one of:

```mermaid
flowchart LR
    A[image  prompt] --> B[dalle3]
    B --> C[image]
    C --> D[dreamgaussian]
    D --> E[blender]
    E --> F[STL file]
    F --> G[3D Printer]

    A[text] -->  Z[Fooocus UI]
    Z --> C
```

## Images

<img src="foocus_images/malinois.png" width="200" /> <img src="foocus_images/mario.png" width="200" /> <img src="foocus_images/moose.png" width="200" /> <img src="foocus_images/tractor.png" width="200" /> <img src="foocus_images/angel.png" width="200" />

## 3D Models in Blender

<img src="3d_models_in_blender.png" width="800">

![blender](blender_models.png)

## Usage

```bash
# Generate images to ./images
python3 get_images.py

# For each PNG, run the dreamgaussian pipeline against it
bash generate_3d_objects.sh <image_directory> <3d_model_output_directory>
```