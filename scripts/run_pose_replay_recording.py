import argparse

from lhpr_vln.config import load_all_configs
from lhpr_vln.task_loader import load_lhpr_task
from lhpr_vln.action_loader import load_action_sequence
from lhpr_vln.pose_loader import (
    flatten_task_json_trials,
    pair_poses_with_actions,
)
from lhpr_vln.habitat_pose_replay import (
    build_default_video_path,
    record_poses,
)


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

    parser.add_argument(
        "--output",
        default=None,
        help="Output video path. Defaults to outputs/replay_videos/<task-name>.mp4",
    )

    parser.add_argument(
        "--show",
        action="store_true",
        help="Also show the replay window while recording.",
    )

    args = parser.parse_args()

    configs = load_all_configs(args.paths, args.sim, args.task)

    task_cfg = configs["task"]
    sim_cfg = configs["simulator"]

    task_bundle = load_lhpr_task(task_cfg)
    action_items = load_action_sequence(task_bundle["trial_dir"])
    pose_items = flatten_task_json_trials(task_bundle["task_json_path"])

    paired_items = pair_poses_with_actions(pose_items, action_items)

    output_path = args.output or build_default_video_path(task_cfg)

    print("=" * 100)
    print("LHPR-VLN POSE-BASED HABITAT REPLAY RECORDING")
    print("=" * 100)

    print("\nInstruction:")
    print(task_cfg["instruction"])

    print("\nScene:")
    print(task_cfg["scene"]["scene_id"])

    print("\nAction folders:", len(action_items))
    print("Pose entries from task.json:", len(pose_items))
    print("Paired replay entries:", len(paired_items))
    print("Output video:", output_path)

    if len(action_items) != len(pose_items):
        print("\nCount mismatch.")
        print("The recording will use the minimum paired count.")

    record_poses(
        task_cfg=task_cfg,
        sim_cfg=sim_cfg,
        paired_items=paired_items,
        output_path=output_path,
        show_window=args.show,
    )


if __name__ == "__main__":
    main()

