import argparse

from lhpr_vln.config import load_all_configs
from lhpr_vln.task_loader import load_lhpr_task
from lhpr_vln.action_loader import load_action_sequence
from lhpr_vln.pose_loader import (
    flatten_task_json_trials,
    pair_poses_with_actions,
)
from lhpr_vln.habitat_pose_replay import replay_poses


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--paths",
        default="configs/paths/local.yaml",
    )

    parser.add_argument(
        "--sim",
        default="configs/simulator/habitat_rgb.yaml",
    )

    parser.add_argument(
        "--task",
        default="configs/replay/batch6_kettle_task.yaml",
    )

    args = parser.parse_args()

    configs = load_all_configs(args.paths, args.sim, args.task)

    task_cfg = configs["task"]
    sim_cfg = configs["simulator"]

    task_bundle = load_lhpr_task(task_cfg)
    action_items = load_action_sequence(task_bundle["trial_dir"])
    pose_items = flatten_task_json_trials(task_bundle["task_json_path"])

    paired_items = pair_poses_with_actions(pose_items, action_items)

    print("=" * 100)
    print("LHPR-VLN POSE-BASED HABITAT REPLAY")
    print("=" * 100)

    print("\nInstruction:")
    print(task_cfg["instruction"])

    print("\nScene:")
    print(task_cfg["scene"]["scene_id"])

    print("\nAction folders:", len(action_items))
    print("Pose entries from task.json:", len(pose_items))
    print("Paired replay entries:", len(paired_items))

    if len(action_items) != len(pose_items):
        print("\n⚠️ Count mismatch.")
        print("The replay will use the minimum paired count.")

    replay_poses(task_cfg, sim_cfg, paired_items)


if __name__ == "__main__":
    main()
