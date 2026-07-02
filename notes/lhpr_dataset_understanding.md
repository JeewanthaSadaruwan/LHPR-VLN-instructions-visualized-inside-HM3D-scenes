# Full LHPR-VLN Dataset Understanding Canvas

## 1. Purpose of This Note

This note explains the structure of the **LHPR-VLN dataset** using the downloaded **Batch 6** data.

The goal is to understand:

```text
How long-horizon VLN tasks are stored
How a full task is decomposed into subtasks
How navigation step-task JSONs are connected to full tasks
How action folders and RGB-D images represent the trajectory
Why the number of expected subtasks and actual step-task JSONs can be different
How this dataset can be used to build a small viewer or prototype
```

This dataset understanding is important before trying:

```text
model inference
model training
trajectory replay
CoT / reasoning visualization
memory-based VLN experiments
```

---

## 2. Current Local Setup

Working directory:

```bash
~/Desktop/LHVLN_scene
```

Active conda environment:

```bash
conda activate habitat-display
```

LHPR-VLN raw downloaded files:

```text
data/lhpr_raw/
├── batch_6.zip
├── step_task.zip
├── task.zip
└── episode_task.zip
```

Extracted dataset:

```text
data/lhpr_extracted/
├── task/
├── step_task/
└── episode_task/
```

For the first experiment, I am focusing only on:

```text
task/batch_6
step_task/batch_6
episode_task/batch_6.json.gz
```

---

## 3. Why Batch 6 Was Used

The full dataset is large, so I checked the size of all ZIP files before downloading.

The smallest trajectory batch was:

```text
batch_6.zip = 3.76 GB
```

Other batches were larger:

```text
batch_1.zip = 10.57 GB
batch_7.zip = 13.98 GB
batch_8.zip = 21.03 GB
```

So Batch 6 was selected because it is enough for the first dataset-understanding experiment.

---

## 4. Three Main Dataset Folders

After extraction, the LHPR-VLN data has three important folders:

```text
data/lhpr_extracted/
├── task/
├── step_task/
└── episode_task/
```

Each folder has a different role.

---

# 5. `task/` Folder

The `task/` folder contains the **main long-horizon task data**.

For Batch 6:

```text
data/lhpr_extracted/task/batch_6/
├── 2/
├── 3/
└── 4/
```

These numbers represent the **number of major navigation stages** in the long-horizon task.

| Folder | Meaning                               |
| ------ | ------------------------------------- |
| `2/`   | 2-navigation-stage long-horizon tasks |
| `3/`   | 3-navigation-stage long-horizon tasks |
| `4/`   | 4-navigation-stage long-horizon tasks |

Important correction:

```text
2, 3, and 4 do not mean only 2, 3, or 4 primitive actions.
They mean the number of main navigation goals/stages in the task.
```

Example:

```text
task/batch_6/2/
└── Bring the toy from the bathroom to the table in the laundry room/
```

The task folder name itself is the **full natural language instruction**.

---

## 6. Example Full Task

Example task:

```text
Bring the toy from the bathroom to the table in the laundry room
```

This task is stored in:

```text
data/lhpr_extracted/task/batch_6/2/
Bring the toy from the bathroom to the table in the laundry room/
```

Inside this task folder:

```text
Bring the toy from the bathroom to the table in the laundry room/
├── config.json
└── success/
    └── trial_1/
        ├── action-step folders
        ├── step-task JSON files
        └── task.json
```

---

# 7. `config.json`

The `config.json` file gives the **full task-level description**.

Example:

```json
{
  "Task instruction": "Bring the toy from the bathroom to the table in the laundry room",
  "Subtask list": [
    "Move_to('toy_8')",
    "Grab('toy')",
    "Move_to('table_9')",
    "Release('toy')"
  ],
  "Robot": "spot",
  "Scene": "00262-1xGrZPxG1Hz",
  "Object": [
    [
      "toy",
      "Region 8: Bathroom"
    ],
    [
      "table",
      "Region 9: Tie: Laundry room & Bathroom"
    ]
  ],
  "Start pos": [
    -8.045344352722168,
    0.11077675223350525,
    0.07300662994384766
  ]
}
```

---

## 8. Meaning of `config.json` Fields

### `Task instruction`

```text
Bring the toy from the bathroom to the table in the laundry room
```

This is the full long-horizon instruction.

---

### `Subtask list`

```text
Move_to('toy_8')
Grab('toy')
Move_to('table_9')
Release('toy')
```

This is the symbolic task breakdown.

| Subtask              | Meaning                            |
| -------------------- | ---------------------------------- |
| `Move_to('toy_8')`   | Navigate to the toy in Region 8    |
| `Grab('toy')`        | Pick up the toy                    |
| `Move_to('table_9')` | Navigate to the table in Region 9  |
| `Release('toy')`     | Place/release the toy at the table |

Important point:

```text
Only Move_to(...) subtasks are navigation subtasks.
Grab and Release are manipulation-style actions.
```

So this full task has:

```text
2 navigation stages:
1. Move to toy
2. Move to table

plus manipulation primitives:
Grab toy
Release toy
```

---

### `Robot`

```text
spot
```

This means the task was designed for a Spot-like robot embodiment.

For my current work, I am not using a real Spot robot.
I am using the dataset to understand the VLN task structure.

---

### `Scene`

```text
00262-1xGrZPxG1Hz
```

This is the HM3D scene ID.

To replay this task in Habitat, I need the matching HM3D scene file locally.

---

### `Object`

```text
toy    → Region 8: Bathroom
table  → Region 9: Laundry room & Bathroom
```

This tells which objects are involved and where they are located.

This is important for long-horizon VLN because the model must understand:

```text
source object
destination object
room/region grounding
object-region relationship
```

---

### `Start pos`

```text
[-8.045344352722168, 0.11077675223350525, 0.07300662994384766]
```

This is the robot’s initial position in the 3D environment.

---

# 9. `success/trial_1/` Folder

Inside each task folder, there is:

```text
success/trial_1/
```

This contains a **successful demonstration trajectory**.

That means the dataset already provides one successful execution path for the task.

Inside `trial_1`, there are:

```text
action-step folders
step-task JSON files
task.json
```

Example action-step folders:

```text
0_turn_left_for_toy/
1_turn_left_for_toy/
2_turn_left_for_toy/
5_move_forward_for_toy/
...
90_turn_left_for_table/
91_stop_for_table/
```

---

## 10. Meaning of Action-Step Folders

Each action-step folder name follows this pattern:

```text
<step number>_<action>_for_<target>
```

Example:

```text
5_move_forward_for_toy
```

Meaning:

```text
Step number: 5
Action: move_forward
Target: toy
```

Example:

```text
91_stop_for_table
```

Meaning:

```text
Step number: 91
Action: stop
Target: table
```

So each folder represents **one executed action step** in the successful trajectory.

---

# 11. Images Inside Each Action-Step Folder

Each action-step folder contains six images:

```text
front.png
left.png
right.png
depth_front.png
depth_left.png
depth_right.png
```

Meaning:

| File              | Meaning                              |
| ----------------- | ------------------------------------ |
| `front.png`       | RGB image from the front camera/view |
| `left.png`        | RGB image from the left camera/view  |
| `right.png`       | RGB image from the right camera/view |
| `depth_front.png` | Depth image from the front view      |
| `depth_left.png`  | Depth image from the left view       |
| `depth_right.png` | Depth image from the right view      |

So for each action step, the dataset provides:

```text
3 RGB angled views:
front, left, right

3 depth angled views:
depth_front, depth_left, depth_right
```

This means the agent has multi-view RGB-D observations at every step.

---

# 12. Step-Task JSON Files Inside `trial_1`

Inside `success/trial_1/`, there are also JSON files for navigation segments.

These are not the full long-horizon task.
They are **individual navigation subtask JSONs**.

Example 1: navigation to toy

```json
{
  "trajectory path": "task/batch_6/2/Bring the toy from the bathroom to the table in the laundry room/success/trial_1",
  "start": 7,
  "end": 63,
  "Robot": "spot",
  "Scene": "00262-1xGrZPxG1Hz",
  "target": [
    "toy"
  ],
  "Region": [
    "8"
  ],
  "start_pos": [
    -8.170344352722168,
    0.11077675223350525,
    0.2895130217075348
  ],
  "start_yaw": 0,
  "Task instruction": "Move forward through the doorway, turn right at the door, then go straight to the room to reach the toy."
}
```

This describes the navigation segment:

```text
Move_to('toy_8')
```

It says:

```text
Use the full trajectory path
Start from step 7
End at step 63
Target is toy
Region is 8
Start from the given position and yaw
Follow the natural language instruction to reach the toy
```

---

Example 2: navigation to table

```json
{
  "trajectory path": "task/batch_6/2/Bring the toy from the bathroom to the table in the laundry room/success/trial_1",
  "start": 69,
  "end": 90,
  "Robot": "spot",
  "Scene": "00262-1xGrZPxG1Hz",
  "target": [
    "table"
  ],
  "Region": [
    "9"
  ],
  "start_pos": [
    -0.6352566480636597,
    0.11077675223350525,
    4.274754524230957
  ],
  "start_yaw": 150,
  "Task instruction": "Move forward through the doorway to reach the table."
}
```

This describes the navigation segment:

```text
Move_to('table_9')
```

It says:

```text
Use the same full trajectory
Start from step 69
End at step 90
Target is table
Region is 9
Start from the given position and yaw
Follow the instruction to reach the table
```

---

## 13. Important Meaning of `start` and `end`

In a step-task JSON:

```json
"start": 145,
"end": 164
```

does **not** mean the subtask has 145 steps.

It means:

```text
This subtask starts at step 145 inside the full long-horizon trajectory
and ends at step 164 inside that same trajectory.
```

Example:

```text
Full trajectory:
0 ───────────────────────────────────────────── 164

Subtask 1:
0 ───── 60

Subtask 2:
70 ───── 130

Subtask 3:
145 ─── 164
```

So if a JSON starts at 145, it is probably a later subtask in a larger long-horizon task.

---

# 14. `task.json`

Inside:

```text
success/trial_1/task.json
```

there is a full trajectory record.

It contains:

```text
Task instruction
Subtask list
Robot
Scene
Object
Region Name
Region
trial
```

Inside `trial`, there may be:

```text
trial_0
trial_1
```

Each trial contains:

```text
pos
yaw
action
```

Meaning:

| Field    | Meaning                          |
| -------- | -------------------------------- |
| `pos`    | Robot 3D position at each step   |
| `yaw`    | Robot heading angle at each step |
| `action` | Action taken at each step        |

Example actions:

```text
turn_left
move_forward
turn_right
stop
```

So `task.json` is useful for replaying the full successful trajectory in Habitat.

---

# 15. `step_task/` Folder

The `step_task/` folder contains a collected index of the navigation-subtask JSON files.

For Batch 6:

```text
data/lhpr_extracted/step_task/batch_6/
├── <navigation instruction>.json
├── <navigation instruction>.json
└── ...
```

These files are similar to the step-task JSONs inside:

```text
task/batch_6/.../success/trial_1/
```

But `step_task/batch_6/` collects all navigation subtasks from Batch 6 in one place.

Important:

```text
step_task/ does not contain RGB or depth images.
It only contains JSON metadata for navigation segments.
```

---

## 16. Difference Between `task/` and `step_task/`

| Location                                            | Meaning                                                   |
| --------------------------------------------------- | --------------------------------------------------------- |
| `task/batch_6/.../config.json`                      | Full long-horizon task and high-level subtask list        |
| `task/batch_6/.../success/trial_1/`                 | Full successful trajectory with images                    |
| `task/batch_6/.../success/trial_1/<step-task>.json` | Navigation segment JSON inside the actual task folder     |
| `step_task/batch_6/<step-task>.json`                | Separate collected copy/index of navigation segment JSONs |

Correct mental model:

```text
task/batch_6/
= full long-horizon tasks

step_task/batch_6/
= extracted navigation subtasks from those full tasks
```

---

# 17. `episode_task/` Folder

The `episode_task/` folder contains compressed episode-level metadata.

For Batch 6:

```text
data/lhpr_extracted/episode_task/batch_6.json.gz
```

This is useful later when connecting the dataset to Habitat-style episodes or evaluation pipelines.

For the current dataset-understanding stage, the most important folders are:

```text
task/batch_6/
step_task/batch_6/
```

---

# 18. Count Analysis for Batch 6

Batch 6 contains:

```text
2-stage tasks: 17
3-stage tasks: 18
4-stage tasks: 5
```

Total full tasks:

```text
17 + 18 + 5 = 40
```

However, the count script found:

```text
Total tasks from config files: 41
Expected Move_to subtasks from config.json: 110
Actual step-task JSONs inside success/trial_1: 94
Actual JSONs inside step_task/batch_6: 94
Mismatched tasks: 12
```

Important point:

```text
step_task/batch_6 has exactly the same number of JSONs as the step-task JSONs inside success/trial_1.
```

So `step_task/batch_6` is not missing files.

---

## 19. Why Expected Count and Actual Count Are Different

At first, the expected number of navigation subtasks was calculated from the task categories.

For example:

```text
2-stage tasks should roughly have 2 navigation subtasks each
3-stage tasks should roughly have 3 navigation subtasks each
4-stage tasks should roughly have 4 navigation subtasks each
```

But the actual saved JSON count is lower.

Reason:

```text
config.json contains the full symbolic plan.
step_task JSONs contain only the actual saved navigation segments.
```

Some `Move_to(...)` subtasks may not be saved separately because:

```text
the target may already be nearby
the movement may be very short
a navigation segment may be merged with the previous segment
the step-task may be filtered during dataset generation
some stages may not have separate natural language step instructions
```

Therefore:

```text
Expected Move_to subtasks from config.json = 110
Actual saved navigation segment JSONs = 94
```

The correct usable number for Batch 6 step-level navigation is:

```text
94 navigation subtask JSONs
```

---

# 20. Correct Rule for Counting

Do not rely only on:

```text
folder category number × number of tasks
```

Instead, trust the actual files:

```bash
find data/lhpr_extracted/task/batch_6 -path "*/success/trial_1/*.json" ! -name "task.json" | wc -l
```

This gave:

```text
94
```

And:

```bash
find data/lhpr_extracted/step_task/batch_6 -name "*.json" | wc -l
```

also gave:

```text
94
```

Therefore:

```text
The saved navigation subtasks are consistent.
The correct actual number is 94.
```

---

# 21. Three-Level Representation of One Task

One LHPR-VLN task has three main levels.

```text
Level 1: config.json
Full long-horizon task description and symbolic subtask list

Level 2: step-task JSONs
Individual navigation segments with start/end step ranges

Level 3: action-step folders + task.json
Full trajectory with RGB-D observations, positions, yaw, and actions
```

Simplified:

```text
config.json
= what the full task is

step-task JSONs
= how navigation parts are split

success/trial_1 folders
= what the robot saw and did at each step

task.json
= complete trajectory record
```

---

# 22. Full Flow of One Task

Example:

```text
Bring the toy from the bathroom to the table in the laundry room
```

Full high-level symbolic plan:

```text
Move_to toy
Grab toy
Move_to table
Release toy
```

Navigation segment 1:

```text
Move to toy
Steps 7–63
Target: toy
Region: 8
```

Navigation segment 2:

```text
Move to table
Steps 69–90
Target: table
Region: 9
```

Full execution:

```text
Start
↓
Navigate to toy
↓
Grab toy
↓
Navigate to table
↓
Release toy
↓
Stop
```

---

# 23. How This Connects to VLN

This dataset represents VLN as:

```text
Instruction
+ visual observation
+ action history
+ target/subtask state
↓
VLN model
↓
next action
```

Each action step gives the model:

```text
front RGB
left RGB
right RGB
front depth
left depth
right depth
previous action
current target
task instruction
```

The model learns or predicts actions such as:

```text
turn_left
turn_right
move_forward
stop
```

---

# 24. How This Connects to Long-Horizon VLN

Normal VLN often focuses on one instruction and one navigation goal.

LHPR-VLN is harder because the agent must complete multiple connected stages.

The agent must understand:

```text
What is the full instruction?
What object should I go to first?
What should I do after reaching the object?
Which object/room should I remember?
What is the next target?
Have I completed the current subtask?
Should I stop or continue?
```

So LHPR-VLN requires:

```text
instruction decomposition
subtask tracking
object grounding
room/region grounding
memory
visual navigation
progress verification
```

---

# 25. How This Connects to CoT / Reasoning

A reasoning or CoT-style system could use the dataset like this:

```text
Full task instruction
+ current step-task instruction
+ current RGB-D observation
+ current target
+ action history
+ memory
↓
reasoning/planner module
↓
next action suggestion
```

Example reasoning:

```text
The full task is to bring the toy to the table.
The current active subtask is to reach the toy.
The target object is toy in Region 8.
The robot should continue through the doorway and turn right.
The next action should be move_forward.
```

This reasoning can guide a VLN action model.

---

# 26. Useful Commands

Check top-level extracted folders:

```bash
find data/lhpr_extracted -maxdepth 1 -type d
```

Check Batch 6 categories:

```bash
find data/lhpr_extracted/task/batch_6 -maxdepth 1 -type d
```

Count full tasks in each category:

```bash
find data/lhpr_extracted/task/batch_6/2 -mindepth 1 -maxdepth 1 -type d | wc -l
find data/lhpr_extracted/task/batch_6/3 -mindepth 1 -maxdepth 1 -type d | wc -l
find data/lhpr_extracted/task/batch_6/4 -mindepth 1 -maxdepth 1 -type d | wc -l
```

Find task config files:

```bash
find data/lhpr_extracted/task/batch_6 -name "config.json" | head -20
```

Find full trajectory records:

```bash
find data/lhpr_extracted/task/batch_6 -name "task.json" | head -20
```

Count saved step-task JSONs inside task folders:

```bash
find data/lhpr_extracted/task/batch_6 -path "*/success/trial_1/*.json" ! -name "task.json" | wc -l
```

Count collected step-task JSONs:

```bash
find data/lhpr_extracted/step_task/batch_6 -name "*.json" | wc -l
```

Check one trial folder:

```bash
find "data/lhpr_extracted/task/batch_6/2/Bring the toy from the bathroom to the table in the laundry room/success/trial_1" -maxdepth 1 -type d | head -30
```

---

# 27. Next Practical Step

The next step is to build a **single-task Batch 6 viewer**.

The viewer should:

```text
read config.json
read task.json
list action-step folders in correct order
parse step number, action, and target from folder names
display front / left / right RGB images
display depth images
print current step
print current action
print current target
print current subtask
print robot position and yaw if available
```

Expected viewer output:

```text
Task:
Bring the toy from the bathroom to the table in the laundry room

Scene:
00262-1xGrZPxG1Hz

Subtasks:
Move_to toy
Grab toy
Move_to table
Release toy

Current step:
5_move_forward_for_toy

Action:
move_forward

Target:
toy

Images:
front.png
left.png
right.png
depth_front.png
depth_left.png
depth_right.png
```

---

# 28. Final Understanding

The LHPR-VLN Batch 6 dataset provides everything needed to understand long-horizon VLN task execution.

For each task, it gives:

```text
full natural language instruction
symbolic subtask decomposition
HM3D scene ID
robot start position
object and region mapping
successful trajectory
action-step folders
RGB-D observations
step-level navigation instructions
full position/yaw/action trajectory record
```

The most important final idea is:

```text
config.json gives the full task plan.
step-task JSONs give actual saved navigation segments.
success/trial_1 gives visual observations and actions.
task.json gives the complete trajectory record.
```

Therefore, Batch 6 is enough to build the first LHPR-VLN visualization and analysis tool before moving to model inference or training.
