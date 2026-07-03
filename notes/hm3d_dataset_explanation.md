# HM3D Dataset Explanation

## 1. What HM3D Is

HM3D means Habitat-Matterport 3D.

It is a dataset of real indoor 3D environments. These scenes are used with Habitat-Sim and Habitat-Lab to train and test embodied AI agents.

Embodied AI means an agent is placed inside a 3D environment and must act inside it. For example:

- move through a house
- follow a language instruction
- go to a chair
- find an object
- navigate from one room to another
- generate camera observations from a scene

In this project, HM3D provides the 3D world. Habitat provides the simulator/viewer. LHPR/VLN tasks provide language instructions and navigation goals.

## 2. Basic Mental Model

Think of the dataset like this:

```text
HM3D dataset
  -> many indoor scenes
      -> each scene is one building or home-like space
      -> each scene has visual geometry
      -> each scene may have semantic labels
      -> each scene may have navigation data
```

For one scene, the important files are usually:

```text
00800-TEEsavR23oF/
  TEEsavR23oF.basis.glb
  TEEsavR23oF.basis.navmesh
  TEEsavR23oF.semantic.glb
  TEEsavR23oF.semantic.txt
```

## 3. Dataset Splits

HM3D is usually divided into splits:

```text
train/
val/
test/
minival/
```

Meaning:

- `train`: used for model training
- `val`: used for validation during development
- `test`: used for final evaluation
- `minival`: a smaller validation subset

In this workspace, most of the local scene files are under:

```text
/home/js/Desktop/datasets/hm3d/val/
```

So this project is mainly using validation scenes.

## 4. Important HM3D File Types

### `.basis.glb`

Example:

```text
/home/js/Desktop/datasets/hm3d/val/00800-TEEsavR23oF/TEEsavR23oF.basis.glb
```

This is the main 3D scene model.

It contains the visual building geometry and textures. This is what Habitat renders when you open the scene in the viewer or render images using Python.

Simple meaning:

```text
.basis.glb = what the scene looks like
```

### `.basis.navmesh`

Example:

```text
TEEsavR23oF.basis.navmesh
```

This is the navigation mesh.

It tells Habitat where the agent can walk. The agent cannot simply move anywhere inside the 3D model. It needs valid walkable areas.

For example, the navmesh helps answer:

- Is this point on the floor?
- Can the robot stand here?
- Is there a valid path from the start point to the target?
- What is the shortest path through the scene?

Simple meaning:

```text
.basis.navmesh = where the agent is allowed to walk
```

### `.semantic.glb`

Example:

```text
TEEsavR23oF.semantic.glb
```

This file contains semantic geometry.

It helps Habitat know which parts of the scene correspond to labeled objects or regions. For example, some geometry may be labeled as wall, floor, bed, chair, table, door, cabinet, and so on.

Important point:

The agent does not automatically understand a command like `move to the chair` just because `semantic.glb` exists. Your code must still query the semantic scene and connect the language word `chair` to a semantic object.

Simple meaning:

```text
.semantic.glb = labeled object or region geometry
```

### `.semantic.txt`

Example:

```text
TEEsavR23oF.semantic.txt
```

This is a text file that lists semantic labels.

In your scene, it contains entries like:

```text
HM3D Semantic Annotations
1,97C517,"ceiling",1
2,07576C,"wall",1
4,D8DB3A,"door",1
16,1C9E7F,"bed",1
30,3CD850,"armchair",1
```

The rough meaning of each row is:

```text
semantic_id, color, category_or_label, region_id
```

For example:

```text
30,3CD850,"armchair",1
```

means there is a semantic element with ID `30`, color `3CD850`, label `armchair`, and region `1`.

Simple meaning:

```text
.semantic.txt = text labels for semantic objects/regions
```

## 5. Scene Dataset Config JSON

This project has:

```text
/home/js/Desktop/datasets/hm3d/hm3d_annotated_basis.scene_dataset_config.json
```

This file tells Habitat how the HM3D dataset is organized.

It contains paths such as:

```text
val/00800-TEEsavR23oF/*.basis.glb
val/00802-wcojb4TFT35/*.basis.glb
val/00803-k1cupFYWXJ6/*.basis.glb
```

Habitat uses this config to know which scene files are valid and where to find them.

Simple meaning:

```text
scene_dataset_config.json = map that tells Habitat where the scenes are
```

## 6. How Habitat Uses HM3D

Habitat loads an HM3D scene into a simulator.

The usual flow is:

```text
.basis.glb
  -> load visual 3D scene

.basis.navmesh
  -> load walkable navigation area

.semantic.glb + .semantic.txt
  -> load semantic labels if available

Habitat-Sim
  -> create agent
  -> attach camera sensors
  -> move agent
  -> render RGB/depth/semantic observations
```

Your headless rendering script does this kind of work:

```text
examples/render_hm3d_scene.py
```

It:

1. loads one `.basis.glb` scene
2. creates a Habitat simulator
3. creates an RGB camera
4. samples random navigable points
5. renders images
6. saves them to `outputs/`

## 7. Interactive Viewer Workflow

Your script:

```text
open_hm3d_viewer.sh
```

opens an HM3D scene using `habitat-viewer`.

It does these things:

1. loads conda
2. activates the `habitat-display` environment
3. moves into the project folder
4. sets the desktop display
5. points to the HM3D dataset config
6. points to one `.basis.glb` scene
7. opens the scene using NVIDIA GPU variables

The important command is:

```bash
habitat-viewer --dataset "$DATASET" --use-default-lighting "$SCENE"
```

This is useful for manually inspecting the scene.

## 8. Headless Rendering Workflow

Your script:

```text
examples/render_hm3d_scene.py
```

renders images without opening the interactive viewer.

It uses:

```python
sim_cfg.scene_id = scene_path
```

to load an HM3D scene.

Then it creates a camera sensor:

```python
rgb_sensor.uuid = "color_sensor"
rgb_sensor.sensor_type = habitat_sim.SensorType.COLOR
rgb_sensor.resolution = [512, 512]
rgb_sensor.position = [0.0, 1.5, 0.0]
```

Then it samples random valid positions:

```python
position = sim.pathfinder.get_random_navigable_point()
```

That function depends on the navmesh. It chooses a point where the agent can stand.

The script saves outputs like:

```text
outputs/hm3d_view_0.png
outputs/hm3d_view_1.png
outputs/hm3d_view_2.png
```

## 9. Can Semantic Data Locate a Chair?

Short answer: yes, but not automatically.

Suppose the instruction is:

```text
move to the chair
```

The semantic files can help, but your code must do the reasoning.

The full pipeline is:

```text
instruction: "move to the chair"
  -> extract target word: "chair"
  -> search semantic scene for object labels like "chair" or "armchair"
  -> get object position or bounding box center
  -> find a nearby navigable point on the navmesh
  -> plan path to that point
  -> move the agent
```

Important distinction:

```text
.semantic.glb/.semantic.txt = object/region labels
.basis.navmesh = valid walking locations
```

So semantic data may tell you where the chair is, but the navmesh tells you where the robot can stand near the chair.

## 10. Why Object Location Is Not Always Simple

There are a few practical problems:

- The label may be `armchair` instead of `chair`.
- Some labels may be noisy or missing.
- A large object may have multiple semantic parts.
- The object center may be inside the object, not on the floor.
- A target object may not be reachable directly.
- The closest navigable point must be computed using the navmesh.

So the correct goal is usually not:

```text
go exactly to object center
```

but:

```text
go to a navigable point near the object
```

## 11. Relation To LHPR/VLN Tasks

LHPR/VLN data gives language tasks and trajectory information.

One of your step-task JSON files contains fields like:

```json
{
  "Scene": "00269-JNiWU5TZLtt",
  "target": ["shelf"],
  "Region": ["8"],
  "start_pos": [-3.4830431938171387, 0.0724058449268341, -39.794551849365234],
  "start_yaw": -30,
  "Task instruction": "Move forward across the hardwood room, then turn left at the rocking chair..."
}
```

This means the task gives useful navigation information:

- `Scene`: which HM3D scene the task belongs to
- `target`: target object or goal category
- `Region`: target region information
- `start_pos`: agent start position
- `start_yaw`: starting direction
- `Task instruction`: natural language instruction

The connection is:

```text
LHPR/VLN task
  -> says what to do in language
  -> gives scene ID and start/target info

HM3D scene
  -> provides the 3D environment
  -> provides visual geometry, semantic labels, and navigation mesh

Habitat
  -> loads the scene
  -> places the agent
  -> renders observations
  -> supports navigation and path planning
```

## 12. Full Project Picture

Your project is moving toward this pipeline:

```text
1. Download LHPR/VLN task data
2. Extract task JSON files
3. Match each task to an HM3D scene
4. Load the HM3D scene in Habitat
5. Place the agent at the task start position
6. Read the language instruction
7. Use semantic and navigation data to understand targets
8. Render views or simulate navigation
```

## 13. Useful Commands In This Project

Open the interactive HM3D viewer:

```bash
./open_hm3d_viewer.sh
```

Run the headless renderer:

```bash
conda activate lhvln
python examples/render_hm3d_scene.py
```

Render a different scene by setting `SCENE`:

```bash
SCENE="/home/js/Desktop/datasets/hm3d/val/00800-TEEsavR23oF/TEEsavR23oF.basis.glb" \
python examples/render_hm3d_scene.py
```

List Python package versions:

```bash
python -m pip list
```

Check one package:

```bash
python -m pip show huggingface_hub
```

## 14. One-Line Summary

HM3D gives the 3D indoor world, semantic files describe labeled objects/regions, navmesh files describe where an agent can walk, Habitat runs the simulation, and LHPR/VLN tasks provide language instructions and start/goal information.

