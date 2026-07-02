# LHVLN Scene Rendering

This repo includes two ways to render HM3D scenes:

1. Habitat-display 3D rendering version (interactive viewer)
2. Headless rendering version (image generation script)

## 1) Run Habitat-display 3D Rendering Version

Use this when you want to launch the interactive 3D viewer.

```bash
conda activate habitat-display
cd ~/Desktop/LHVLN_scene

export DISPLAY=:0

DATASET="data/scene_datasets/hm3d/hm3d_annotated_basis.scene_dataset_config.json"
SCENE="data/scene_datasets/hm3d/val/00887-hyFzGGJCSYs/hyFzGGJCSYs.basis.glb"

__NV_PRIME_RENDER_OFFLOAD=1 \
__GLX_VENDOR_LIBRARY_NAME=nvidia \
__VK_LAYER_NV_optimus=NVIDIA_only \
habitat-viewer --dataset "$DATASET" --use-default-lighting "$SCENE"
```

## 2) Run Headless Rendering Version

If you want to run the headless version, activate the `lhvln` environment and run the renderer.
The script now uses a default HM3D scene path, so this single command is enough.

```bash
conda activate lhvln
cd ~/Desktop/LHVLN_scene

python ./examples/render_hm3d_scene.py
```
