from pathlib import Path

from lhpr_vln.task_loader import load_json


def sort_trial_name(name):
    """
    Sort trial_0, trial_1, trial_2...
    """
    try:
        return int(name.split("_")[-1])
    except Exception:
        return 10**9


def flatten_task_json_trials(task_json_path):
    """
    Read task.json and flatten all trial entries into one continuous pose list.

    Each output item contains:
    - global_index
    - source_trial
    - local_index
    - pos
    - yaw
    - action_from_task_json
    """
    task_json_path = Path(task_json_path)
    task_data = load_json(task_json_path)

    trials = task_data.get("trial", {})

    pose_items = []
    global_index = 0

    for trial_name in sorted(trials.keys(), key=sort_trial_name):
        trial = trials[trial_name]

        pos_list = trial.get("pos", [])
        yaw_list = trial.get("yaw", [])
        action_list = trial.get("action", [])

        n = min(len(pos_list), len(yaw_list), len(action_list))

        for i in range(n):
            pose_items.append(
                {
                    "global_index": global_index,
                    "source_trial": trial_name,
                    "local_index": i,
                    "pos": pos_list[i],
                    "yaw": yaw_list[i],
                    "action_from_task_json": action_list[i],
                }
            )
            global_index += 1

    return pose_items


def pair_poses_with_actions(pose_items, action_items):
    """
    Pair flattened task.json poses with sorted action folders.

    If counts are different, pair only the minimum count.
    """
    n = min(len(pose_items), len(action_items))

    paired = []

    for i in range(n):
        paired.append(
            {
                "index": i,
                "pose": pose_items[i],
                "action_folder": action_items[i],
            }
        )

    return paired
