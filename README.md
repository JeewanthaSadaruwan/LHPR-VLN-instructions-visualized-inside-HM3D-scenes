# LHPR-VLN HM3D Replay

A lightweight Habitat-Sim replay tool for visualizing **LHPR-VLN long-horizon navigation instructions** inside **HM3D scenes**.

This project loads an LHPR-VLN task, reads the saved trajectory pose data from `task.json`, places a simple Habitat agent inside the corresponding HM3D scene, and replays the robot movement using the saved position and yaw values.

The current focus is **dataset understanding and trajectory visualization**, not model inference or training.

---

## Demo

<img
  src="assets/batch6_kettle_replay.gif"
  alt="Batch 6 kettle-to-coffee-table replay"
  width="100%"
/>

```text
Instruction:
Could you take the kettle from the kitchen and place it on the coffee table in the living room
```


## Project Goal

The goal of this project is to understand how a long-horizon VLN instruction is executed inside an HM3D environment.

Example instruction:

```text
Could you take the kettle from the kitchen and place it on the coffee table in the living room
```

The system follows this pipeline:

```text
Load LHPR-VLN task
↓
Load HM3D scene and navmesh
↓
Read saved position/yaw/action data from task.json
↓
Set the Habitat agent pose directly at each step
↓
Render the trajectory in a viewer window
```

---

## Current Features

- Loads LHPR-VLN task configuration from YAML files
- Loads HM3D `.basis.glb` scene files
- Loads HM3D `.basis.navmesh` navigation mesh files
- Reads LHPR-VLN `config.json`
- Reads LHPR-VLN `task.json`
- Reads step-task JSON files
- Reads and sorts action-step folders
- Checks RGB-D image availability
- Detects duplicate action-step numbers
- Replays saved trajectory using `task.json` position and yaw values
- Supports yaw correction using `yaw_sign` and `yaw_offset`
- Compares Habitat-rendered frames against dataset `front.png` images

---

## What This Project Does

This project performs **pose-based trajectory replay**.

Instead of predicting actions using a model, it uses the saved ground-truth trajectory from the LHPR-VLN dataset.

```text
task.json position + yaw
↓
Habitat agent pose
↓
Rendered scene frame
```

This allows us to visualize how the instruction is executed inside the HM3D scene.

---

## What This Project Does Not Do Yet

- No VLN model inference
- No model training
- No LLM/CoT reasoning yet
- No visible Spot robot body
- No URDF-based robot simulation
- No physical robot deployment

The current agent is a simple first-person Habitat navigation agent.

---

## Example Task Used

The current configured task is from LHPR-VLN Batch 6.

```text
Instruction:
Could you take the kettle from the kitchen and place it on the coffee table in the living room

Scene:
00843-DYehNKdT76V

Robot:
spot

Subtasks:
Move_to('kettle_8')
Grab('kettle')
Move_to('coffee table_7')
Release('kettle')
```

The current replay uses a simple Habitat agent, not a visible Spot URDF robot.

---

## Usage

### 1. Check Config Files

Run:

```bash
python scripts/check_configs.py
```

This verifies that:

```text
YAML files can be loaded
task_dir exists
config.json exists
success/trial_1 exists
task.json exists
HM3D .basis.glb exists
HM3D .basis.navmesh exists
```

Expected final result:

```text
All required config paths are valid.
```

---

### 2. Check LHPR Task Loading

Run:

```bash
python scripts/check_task_loading.py
```

This checks:

```text
config.json
task.json
step-task JSONs
action-step folders
RGB-D image availability
duplicate step numbers
step-task ranges
```

Example output:

```text
Expected Move_to subtasks:
2

Actual step-task JSON count:
2

Total action folders:
136

All action folders contain required RGB-D images.
```

---

### 3. Run Pose-Based Replay

Run:

```bash
python scripts/run_pose_replay.py
```

If the viewer needs NVIDIA GPU offload:

```bash
__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia python scripts/run_pose_replay.py
```

This opens a Habitat viewer and replays the saved LHPR-VLN trajectory using `task.json` position and yaw values.

---

### 4. Verify Replay Against Dataset Images

Run:

```bash
python scripts/verify_pose_against_dataset.py
```

This compares:

```text
Habitat-rendered frame from task.json pose
vs
Dataset saved front.png
```

The output images are saved under:

```text
outputs/verification/
```

Use these side-by-side images to confirm whether the pose and yaw are aligned correctly.
