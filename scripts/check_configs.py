import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from lhpr_vln.config import load_all_configs, check_required_paths


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--paths",
        default="configs/paths/local.yaml",
        help="Path to local paths YAML",
    )

    parser.add_argument(
        "--sim",
        default="configs/simulator/habitat_rgb.yaml",
        help="Path to simulator YAML",
    )

    parser.add_argument(
        "--task",
        default="configs/replay/batch6_kettle_task.yaml",
        help="Path to replay task YAML",
    )

    args = parser.parse_args()

    configs = load_all_configs(args.paths, args.sim, args.task)

    paths_cfg = configs["paths"]
    sim_cfg = configs["simulator"]
    task_cfg = configs["task"]

    print("=" * 100)
    print("LHPR-VLN CONFIG CHECK")
    print("=" * 100)

    print("\n[1] Loaded YAML files")
    print("✅ paths:", args.paths)
    print("✅ simulator:", args.sim)
    print("✅ task:", args.task)

    print("\n[2] Task information")
    print("Name:", task_cfg["name"])
    print("Batch:", task_cfg["batch"])
    print("Category:", task_cfg["category"])
    print("Instruction:")
    print(task_cfg["instruction"])

    print("\n[3] Scene information")
    print("Scene ID:", task_cfg["scene"]["scene_id"])
    print("GLB:", task_cfg["scene"]["glb"])
    print("Navmesh:", task_cfg["scene"]["navmesh"])

    print("\n[4] Robot information")
    print("Robot type:", task_cfg["robot"]["type"])
    print("Use URDF:", task_cfg["robot"]["use_urdf"])

    print("\n[5] Start state")
    print("Position:", task_cfg["start"]["position"])
    print("Yaw:", task_cfg["start"]["yaw"])

    print("\n[6] Simulator settings")
    print("RGB sensor UUID:", sim_cfg["sensor"]["rgb"]["uuid"])
    print("RGB resolution:", sim_cfg["sensor"]["rgb"]["width"], "x", sim_cfg["sensor"]["rgb"]["height"])
    print("Move forward amount:", sim_cfg["actions"]["move_forward"]["amount"])
    print("Turn left amount:", sim_cfg["actions"]["turn_left"]["amount"])
    print("Turn right amount:", sim_cfg["actions"]["turn_right"]["amount"])
    print("Viewer FPS:", sim_cfg["viewer"]["fps"])

    print("\n[7] Required path checks")

    checks = check_required_paths(configs)

    all_ok = True

    for name, path in checks.items():
        if Path(path).exists():
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}: {path}")
            all_ok = False

    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)

    if all_ok:
        print("✅ All required config paths are valid.")
        print("Next step: create the task/action loader modules.")
    else:
        print("❌ Some paths are invalid. Fix the YAML before continuing.")


if __name__ == "__main__":
    main()
