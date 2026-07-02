import json
from pathlib import Path

BATCH_ROOT = Path("data/lhpr_extracted/task/batch_6")
HM3D_ROOT = Path("data/scene_datasets/hm3d")

# Collect all local HM3D scene IDs from folder names
local_scene_ids = set()

for p in HM3D_ROOT.rglob("*"):
    if p.is_dir():
        name = p.name
        # HM3D folders look like 00800-TEEsavR23oF
        if "-" in name and len(name.split("-")) >= 2:
            local_scene_ids.add(name)

print(f"Local HM3D scene folders found: {len(local_scene_ids)}")

matched = []
missing = []

for cfg_path in BATCH_ROOT.rglob("config.json"):
    task_dir = cfg_path.parent

    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    scene = cfg.get("Scene")

    if scene in local_scene_ids:
        matched.append((task_dir, scene, cfg.get("Task instruction")))
    else:
        missing.append((task_dir, scene, cfg.get("Task instruction")))

print("\nMatched LHPR-VLN tasks with local HM3D scenes:")
print("=" * 80)

for i, (task_dir, scene, instr) in enumerate(matched[:50]):
    print(f"\n[{i}] Scene: {scene}")
    print(f"Instruction: {instr}")
    print(f"Path: {task_dir}")

print("\n" + "=" * 80)
print(f"Total matched tasks: {len(matched)}")
print(f"Total missing-scene tasks: {len(missing)}")