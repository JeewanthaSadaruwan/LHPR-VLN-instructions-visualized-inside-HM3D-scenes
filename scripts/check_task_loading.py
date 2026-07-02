import argparse
import json

from lhpr_vln.config import load_all_configs
from lhpr_vln.task_loader import load_lhpr_task, summarize_task
from lhpr_vln.action_loader import (
    load_action_sequence,
    summarize_actions,
    find_duplicate_step_numbers,
    count_missing_images,
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

    args = parser.parse_args()

    configs = load_all_configs(args.paths, args.sim, args.task)

    task_bundle = load_lhpr_task(configs["task"])
    task_summary = summarize_task(task_bundle)

    action_items = load_action_sequence(task_bundle["trial_dir"])
    action_summary = summarize_actions(action_items)

    duplicates = find_duplicate_step_numbers(action_items)
    missing_images = count_missing_images(action_items)

    print("=" * 100)
    print("LHPR-VLN TASK + ACTION LOADING CHECK")
    print("=" * 100)

    print("\n[1] Task summary")
    print("Instruction:")
    print(task_summary["instruction"])

    print("\nScene:")
    print(task_summary["scene"])

    print("\nRobot:")
    print(task_summary["robot"])

    print("\nStart position:")
    print(task_summary["start_pos"])

    print("\nObjects:")
    print(json.dumps(task_summary["objects"], indent=2))

    print("\nSubtask list:")
    for s in task_summary["subtask_list"]:
        print(" -", s)

    print("\nExpected Move_to subtasks:")
    print(task_summary["expected_move_to_count"])

    print("\nActual step-task JSON count:")
    print(task_summary["actual_step_task_json_count"])

    print("\n[2] Step-task JSONs")

    for i, step_task in enumerate(task_bundle["step_tasks"]):
        print("\n" + "-" * 80)
        print(f"Step-task {i}")
        print("File:", step_task["file_name"])
        print("Target:", step_task["target"])
        print("Region:", step_task["region"])
        print("Start step:", step_task["start"])
        print("End step:", step_task["end"])
        print("Start yaw:", step_task["start_yaw"])
        print("Instruction:")
        print(step_task["instruction"])

    print("\n[3] Action folder summary")
    print("Total action folders:", action_summary["total_action_folders"])

    print("\nAction counts:")
    print(json.dumps(action_summary["action_counts"], indent=2))

    print("\nTarget counts:")
    print(json.dumps(action_summary["target_counts"], indent=2))

    print("\nFirst 10 action folders:")
    for f in action_summary["first_10"]:
        print(" -", f)

    print("\nLast 10 action folders:")
    for f in action_summary["last_10"]:
        print(" -", f)

    print("\n[4] Duplicate step number check")

    if duplicates:
        print(f"Duplicate step numbers found: {len(duplicates)}")

        for step, folders in duplicates.items():
            print(f"\nStep {step}:")
            for folder in folders:
                print(" -", folder)
    else:
        print("No duplicate step numbers found.")

    print("\n[5] Image check")

    if missing_images:
        print(f"Missing image files found: {len(missing_images)}")

        for record in missing_images[:50]:
            print(
                f" - {record['folder']}: missing {record['missing_image']}"
            )
    else:
        print("All action folders contain required RGB-D images.")

    print("\n[6] Step-task range check")

    for i, step_task in enumerate(task_bundle["step_tasks"]):
        start = step_task["start"]
        end = step_task["end"]
        target = step_task["target"]

        matching_actions = [
            item for item in action_items
            if item["parsed"]["step"] >= start
            and item["parsed"]["step"] <= end
        ]

        print("\n" + "-" * 80)
        print(f"Step-task {i}")
        print("Target:", target)
        print("Range:", start, "to", end)
        print("Action folders inside this range:", len(matching_actions))

        if matching_actions:
            print("First action in range:", matching_actions[0]["folder"])
            print("Last action in range :", matching_actions[-1]["folder"])

    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)

    if not missing_images:
        print("✅ Task data and action folders loaded successfully.")
    else:
        print("⚠️ Task loaded, but some images are missing.")

    print("Next step: create Habitat simulator/replay module.")


if __name__ == "__main__":
    main()