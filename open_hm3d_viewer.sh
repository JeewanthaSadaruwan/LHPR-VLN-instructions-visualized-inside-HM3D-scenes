#!/usr/bin/env bash
set -e

# Load conda
source /home/js/miniconda3/etc/profile.d/conda.sh

# Activate display Habitat environment
conda activate habitat-display

# Go to this project, even when the script is launched from another directory.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Use desktop display
export DISPLAY=:0

# HM3D dataset config
DATASET="$SCRIPT_DIR/data/scene_datasets/hm3d/hm3d_annotated_basis.scene_dataset_config.json"

# HM3D scene path
SCENE="$SCRIPT_DIR/data/scene_datasets/hm3d/val/00800-TEEsavR23oF/TEEsavR23oF.basis.glb"

# Open Habitat viewer using NVIDIA GPU
__NV_PRIME_RENDER_OFFLOAD=1 \
__GLX_VENDOR_LIBRARY_NAME=nvidia \
__VK_LAYER_NV_optimus=NVIDIA_only \
habitat-viewer --dataset "$DATASET" --use-default-lighting "$SCENE"

