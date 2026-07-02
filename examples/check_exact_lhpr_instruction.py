import json
from pathlib import Path

# ============================================================
# Replace this with the EXACT instruction folder name
# ============================================================
FULL_INSTRUCTION = "Bring the toy from the bathroom to the table in the laundry room"

# Optional: set stage category if you know it: "2", "3", or "4"
# If you do not know, keep it as None
STAGE_CATEGORY = "2"

BATCH_ROOT = Path("data/lhpr_extracted/task/batch_6")
STEP_TASK_ROOT = Path("data/lhpr_extracted/step_task/batch_6")
HM3D_ROOT = Path("data/scene_datasets/hm3d/val")

REQUIRED_IMAGES = [
    "front.png",
    "left.png",
    "right.png",
    "depth_front.png",
    "depth_left.png",
    "depth_right.png",
]


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def step_number(path: Path):
    try:
        return int(path.name.split("_")[0])
    except Exception:
        return 10**9


def find_task_dir():
    if STAGE_CATEGORY is not None:
        candidate = BATCH_ROOT / STAGE_CATEGORY / FULL_INSTRUCTION
        if candidate.exists():
            return candidate

    # fallback: search all 2/3/4 folders
    matches = []
    for cfg_path in BATCH_ROOT.rglob("config.json"):
        task_dir = cfg_path.parent
        if task_dir.name == FULL_INSTRUCTION:
            matches.append(task_dir)

    if not matches:
        raise FileNotFoundError(f"No exact task folder found for:\n{FULL_INSTRUCTION}")

    if len(matches) > 1:
        print("Warning: multiple exact matches found. Using first one:")
        for m in matches:
            print(" -", m)

    return matches[0]


def main():
    task_dir = find_task_dir()

    print("=" * 100)
    print("LHPR-VLN EXACT INSTRUCTION CHECK")
    print("=" * 100)

    print("\nSelected task directory:")
    print(task_dir)

    # ------------------------------------------------------------
    # config.json
    # ------------------------------------------------------------
    cfg_path = task_dir / "config.json"
    print("\n[1] config.json")

    if not cfg_path.exists():
        print("❌ Missing config.json")
        return

    print("✅ Found config.json")

    cfg = load_json(cfg_path)

    scene_id = cfg.get("Scene")
    subtasks = cfg.get("Subtask list", [])

    print("\nFull instruction:")
    print(cfg.get("Task instruction"))

    print("\nScene:")
    print(scene_id)

    print("\nRobot:")
    print(cfg.get("Robot"))

    print("\nStart position:")
    print(cfg.get("Start pos"))

    print("\nObjects:")
    print(json.dumps(cfg.get("Object"), indent=2))

    print("\nSubtask list:")
    for s in subtasks:
        print(" -", s)

    expected_move_to = sum(1 for s in subtasks if s.startswith("Move_to"))
    print(f"\nExpected Move_to navigation subtasks: {expected_move_to}")

    # ------------------------------------------------------------
    # HM3D scene check
    # ------------------------------------------------------------
    print("\n[2] Local HM3D scene check")

    scene_matches = list(HM3D_ROOT.rglob(f"*{scene_id}*")) if scene_id else []

    if scene_matches:
        print(f"✅ Found local HM3D scene match(es): {len(scene_matches)}")
        for p in scene_matches[:10]:
            print(" -", p)
    else:
        print("⚠️ No local HM3D scene folder/file found for this scene ID")
        print("Scene needed:", scene_id)

    # ------------------------------------------------------------
    # trial folder
    # ------------------------------------------------------------
    trial_dir = task_dir / "success" / "trial_1"
    print("\n[3] success/trial_1")

    if not trial_dir.exists():
        print("❌ Missing success/trial_1")
        return

    print("✅ Found success/trial_1")

    # ------------------------------------------------------------
    # task.json
    # ------------------------------------------------------------
    print("\n[4] task.json")

    task_json_path = trial_dir / "task.json"

    if not task_json_path.exists():
        print("❌ Missing task.json")
    else:
        print("✅ Found task.json")
        task_data = load_json(task_json_path)

        trials = task_data.get("trial", {})
        print("Trials available:", list(trials.keys()))

        if "trial_1" in trials:
            t = trials["trial_1"]
            print("trial_1 pos count   :", len(t.get("pos", [])))
            print("trial_1 yaw count   :", len(t.get("yaw", [])))
            print("trial_1 action count:", len(t.get("action", [])))

    # ------------------------------------------------------------
    # step-task JSONs inside trial_1
    # ------------------------------------------------------------
    print("\n[5] Step-task JSONs inside trial_1")

    step_jsons = sorted([p for p in trial_dir.glob("*.json") if p.name != "task.json"])

    print(f"Actual step-task JSONs: {len(step_jsons)}")

    for jf in step_jsons:
        data = load_json(jf)

        print("\nJSON:", jf.name)
        print("  target:", data.get("target"))
        print("  region:", data.get("Region"))
        print("  start :", data.get("start"))
        print("  end   :", data.get("end"))
        print("  instr :", data.get("Task instruction"))

        indexed_copy = STEP_TASK_ROOT / jf.name
        if indexed_copy.exists():
            print("  ✅ matching file exists in step_task/batch_6")
        else:
            print("  ⚠️ matching file missing in step_task/batch_6")

    if len(step_jsons) == expected_move_to:
        print("\n✅ Actual step-task count matches expected Move_to count")
    else:
        print("\n⚠️ Actual step-task count does not match expected Move_to count")
        print("This can be normal if some Move_to stages are merged, very short, or filtered.")

    # ------------------------------------------------------------
    # action-step folders and images
    # ------------------------------------------------------------
    print("\n[6] Action-step folders and image check")

    step_dirs = sorted([p for p in trial_dir.iterdir() if p.is_dir()], key=step_number)

    print(f"Action-step folders found: {len(step_dirs)}")

    missing = []

    for step_dir in step_dirs:
        for img in REQUIRED_IMAGES:
            if not (step_dir / img).exists():
                missing.append((step_dir.name, img))

    if missing:
        print(f"❌ Missing image files: {len(missing)}")
        for step_name, img in missing[:30]:
            print(f" - {step_name}: missing {img}")
    else:
        print("✅ All action-step folders contain the required 6 images")

    print("\nFirst 10 action-step folders:")
    for p in step_dirs[:10]:
        print(" -", p.name)

    print("\nLast 10 action-step folders:")
    for p in step_dirs[-10:]:
        print(" -", p.name)

    # ------------------------------------------------------------
    # final summary
    # ------------------------------------------------------------
    print("\n" + "=" * 100)
    print("FINAL SUMMARY")
    print("=" * 100)

    print("Instruction:", FULL_INSTRUCTION)
    print("Task directory:", task_dir)
    print("Scene:", scene_id)
    print("Expected Move_to subtasks:", expected_move_to)
    print("Actual step-task JSONs:", len(step_jsons))
    print("Action-step folders:", len(step_dirs))
    print("Missing images:", len(missing))

    if cfg_path.exists() and trial_dir.exists() and task_json_path.exists() and not missing:
        print("\n✅ This instruction has the required files for processing/viewing.")
    else:
        print("\n⚠️ Some required parts are missing. Check warnings above.")


if __name__ == "__main__":
    main()