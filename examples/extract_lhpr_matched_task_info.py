import argparse
import json
from pathlib import Path


BATCH_ROOT = Path("/home/js/Desktop/datasets/lhpr/task/batch_6")
STEP_TASK_ROOT = Path("/home/js/Desktop/datasets/lhpr/step_task/batch_6")
HM3D_ROOT = Path("/home/js/Desktop/datasets/hm3d")
OUTPUT_ROOT = Path("outputs/lhpr_task_reports")

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


def collect_local_scene_ids():
    local_scene_ids = set()

    for p in HM3D_ROOT.rglob("*"):
        if p.is_dir():
            name = p.name
            # Example HM3D scene folder: 00861-GLAQ4DNUx5U
            if "-" in name:
                local_scene_ids.add(name)

    return local_scene_ids


def find_scene_paths(scene_id: str):
    scene_paths = []

    for p in HM3D_ROOT.rglob("*"):
        if scene_id in str(p):
            scene_paths.append(p)

    return sorted(scene_paths)


def find_scene_asset_files(scene_id: str):
    scene_matches = find_scene_paths(scene_id)

    glb_files = []
    navmesh_files = []
    semantic_files = []
    config_files = []

    for p in scene_matches:
        if p.is_file():
            if p.name.endswith(".basis.glb") or p.name.endswith(".glb"):
                glb_files.append(p)
            elif p.name.endswith(".navmesh"):
                navmesh_files.append(p)
            elif "semantic" in p.name.lower():
                semantic_files.append(p)
            elif p.name.endswith(".json"):
                config_files.append(p)

    return {
        "all_matches": [str(p) for p in scene_matches],
        "glb_files": [str(p) for p in glb_files],
        "navmesh_files": [str(p) for p in navmesh_files],
        "semantic_files": [str(p) for p in semantic_files],
        "config_files": [str(p) for p in config_files],
    }


def find_matched_tasks():
    local_scene_ids = collect_local_scene_ids()

    matched = []

    for cfg_path in sorted(BATCH_ROOT.rglob("config.json")):
        task_dir = cfg_path.parent
        cfg = load_json(cfg_path)

        scene = cfg.get("Scene")
        instruction = cfg.get("Task instruction", task_dir.name)

        if scene in local_scene_ids:
            matched.append(
                {
                    "task_dir": task_dir,
                    "scene": scene,
                    "instruction": instruction,
                    "category": task_dir.parent.name,
                }
            )

    return matched


def parse_step_folder_name(name: str):
    # Example: 5_move_forward_for_toy
    parts = name.split("_")

    if len(parts) < 4:
        return {
            "raw": name,
            "step": None,
            "action": None,
            "target": None,
        }

    try:
        step = int(parts[0])
    except Exception:
        step = None

    if "for" in parts:
        for_index = parts.index("for")
        action = "_".join(parts[1:for_index])
        target = "_".join(parts[for_index + 1:])
    else:
        action = "_".join(parts[1:])
        target = None

    return {
        "raw": name,
        "step": step,
        "action": action,
        "target": target,
    }


def summarize_task(task_info, index):
    task_dir = task_info["task_dir"]
    cfg_path = task_dir / "config.json"
    trial_dir = task_dir / "success" / "trial_1"
    task_json_path = trial_dir / "task.json"

    cfg = load_json(cfg_path)

    scene_id = cfg.get("Scene")
    subtasks = cfg.get("Subtask list", [])
    expected_move_to = sum(1 for s in subtasks if s.startswith("Move_to"))

    report = {
        "selected_index": index,
        "task_dir": str(task_dir),
        "category": task_info["category"],
        "full_instruction": cfg.get("Task instruction"),
        "scene_id": scene_id,
        "robot": cfg.get("Robot"),
        "start_pos": cfg.get("Start pos"),
        "objects": cfg.get("Object"),
        "subtask_list": subtasks,
        "expected_move_to_count": expected_move_to,
        "hm3d_scene_assets": find_scene_asset_files(scene_id),
        "trial_1_exists": trial_dir.exists(),
        "task_json_exists": task_json_path.exists(),
        "step_task_jsons": [],
        "action_step_folders": [],
        "image_check": {
            "missing_images": [],
            "required_images": REQUIRED_IMAGES,
        },
        "task_json_summary": {},
    }

    # ------------------------------------------------------------
    # Read task.json summary
    # ------------------------------------------------------------
    if task_json_path.exists():
        task_data = load_json(task_json_path)
        trials = task_data.get("trial", {})

        report["task_json_summary"]["available_trials"] = list(trials.keys())

        if "trial_1" in trials:
            t = trials["trial_1"]
            report["task_json_summary"]["trial_1_pos_count"] = len(t.get("pos", []))
            report["task_json_summary"]["trial_1_yaw_count"] = len(t.get("yaw", []))
            report["task_json_summary"]["trial_1_action_count"] = len(t.get("action", []))
            report["task_json_summary"]["trial_1_first_actions"] = t.get("action", [])[:10]
            report["task_json_summary"]["trial_1_last_actions"] = t.get("action", [])[-10:]

    # ------------------------------------------------------------
    # Step-task JSONs
    # ------------------------------------------------------------
    if trial_dir.exists():
        step_jsons = sorted([p for p in trial_dir.glob("*.json") if p.name != "task.json"])

        for jf in step_jsons:
            data = load_json(jf)
            indexed_copy = STEP_TASK_ROOT / jf.name

            report["step_task_jsons"].append(
                {
                    "file": jf.name,
                    "path": str(jf),
                    "exists_in_step_task_folder": indexed_copy.exists(),
                    "indexed_path": str(indexed_copy),
                    "target": data.get("target"),
                    "region": data.get("Region"),
                    "start": data.get("start"),
                    "end": data.get("end"),
                    "start_pos": data.get("start_pos"),
                    "start_yaw": data.get("start_yaw"),
                    "task_instruction": data.get("Task instruction"),
                    "trajectory_path": data.get("trajectory path"),
                }
            )

    # ------------------------------------------------------------
    # Action-step folders and image availability
    # ------------------------------------------------------------
    if trial_dir.exists():
        step_dirs = sorted([p for p in trial_dir.iterdir() if p.is_dir()], key=step_number)

        for sd in step_dirs:
            parsed = parse_step_folder_name(sd.name)

            missing = []
            existing = []

            for img in REQUIRED_IMAGES:
                if (sd / img).exists():
                    existing.append(img)
                else:
                    missing.append(img)
                    report["image_check"]["missing_images"].append(
                        {
                            "step_folder": sd.name,
                            "missing_file": img,
                        }
                    )

            report["action_step_folders"].append(
                {
                    "folder": sd.name,
                    "path": str(sd),
                    "parsed": parsed,
                    "existing_images": existing,
                    "missing_images": missing,
                }
            )

    return report


def print_report(report):
    print("=" * 100)
    print("LHPR-VLN SELECTED TASK INFORMATION")
    print("=" * 100)

    print("\nSelected index:", report["selected_index"])
    print("Category:", report["category"])
    print("Instruction:")
    print(report["full_instruction"])

    print("\nScene ID:")
    print(report["scene_id"])

    print("\nRobot:")
    print(report["robot"])

    print("\nStart position:")
    print(report["start_pos"])

    print("\nObjects:")
    print(json.dumps(report["objects"], indent=2))

    print("\nSubtask list:")
    for s in report["subtask_list"]:
        print(" -", s)

    print("\nExpected Move_to count:", report["expected_move_to_count"])

    print("\nHM3D scene assets:")
    assets = report["hm3d_scene_assets"]

    print("GLB files:")
    for p in assets["glb_files"]:
        print(" -", p)

    print("Navmesh files:")
    for p in assets["navmesh_files"]:
        print(" -", p)

    print("\nStep-task JSONs:")
    print("Count:", len(report["step_task_jsons"]))

    for i, sj in enumerate(report["step_task_jsons"]):
        print("\n", "-" * 80)
        print(f"Step-task {i}")
        print("File:", sj["file"])
        print("Target:", sj["target"])
        print("Region:", sj["region"])
        print("Start step:", sj["start"])
        print("End step:", sj["end"])
        print("Start yaw:", sj["start_yaw"])
        print("Instruction:", sj["task_instruction"])
        print("Exists in step_task folder:", sj["exists_in_step_task_folder"])

    print("\nAction-step folders:")
    print("Count:", len(report["action_step_folders"]))

    print("\nFirst 10 action folders:")
    for item in report["action_step_folders"][:10]:
        p = item["parsed"]
        print(f" - {item['folder']} | action={p['action']} | target={p['target']}")

    print("\nLast 10 action folders:")
    for item in report["action_step_folders"][-10:]:
        p = item["parsed"]
        print(f" - {item['folder']} | action={p['action']} | target={p['target']}")

    missing_images = report["image_check"]["missing_images"]

    print("\nImage check:")
    if missing_images:
        print("Missing images:", len(missing_images))
        for m in missing_images[:20]:
            print(" -", m)
    else:
        print("All action-step folders have the required 6 images.")

    print("\ntask.json summary:")
    print(json.dumps(report["task_json_summary"], indent=2))

    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print("Instruction:", report["full_instruction"])
    print("Scene:", report["scene_id"])
    print("Move_to subtasks expected:", report["expected_move_to_count"])
    print("Step-task JSONs found:", len(report["step_task_jsons"]))
    print("Action-step folders:", len(report["action_step_folders"]))
    print("Missing image count:", len(missing_images))

    if report["hm3d_scene_assets"]["glb_files"]:
        print("HM3D GLB scene: available")
    else:
        print("HM3D GLB scene: not found")

    if report["hm3d_scene_assets"]["navmesh_files"]:
        print("HM3D navmesh: available")
    else:
        print("HM3D navmesh: not found")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--list",
        action="store_true",
        help="List matched tasks whose HM3D scenes are available locally",
    )
    parser.add_argument(
        "--index",
        type=int,
        default=1,
        help="Matched task index to inspect",
    )
    args = parser.parse_args()

    matched = find_matched_tasks()

    if not matched:
        print("No matched tasks found.")
        return

    if args.list:
        print("Matched tasks with local HM3D scenes:")
        print("=" * 100)

        for i, item in enumerate(matched):
            print(f"\n[{i}]")
            print("Scene:", item["scene"])
            print("Category:", item["category"])
            print("Instruction:", item["instruction"])
            print("Path:", item["task_dir"])

        print("\nTotal matched tasks:", len(matched))
        return

    if args.index < 0 or args.index >= len(matched):
        print(f"Invalid index: {args.index}")
        print(f"Available index range: 0 to {len(matched) - 1}")
        return

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    report = summarize_task(matched[args.index], args.index)
    print_report(report)

    out_path = OUTPUT_ROOT / f"task_{args.index:02d}_report.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\nSaved report to:")
    print(out_path)


if __name__ == "__main__":
    main()