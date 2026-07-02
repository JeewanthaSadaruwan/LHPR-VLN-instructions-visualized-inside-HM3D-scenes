from pathlib import Path
from collections import defaultdict


REQUIRED_IMAGES = [
    "front.png",
    "left.png",
    "right.png",
    "depth_front.png",
    "depth_left.png",
    "depth_right.png",
]


def parse_action_folder_name(folder_name):
    """
    Parse action-step folder names.

    Example:
    5_move_forward_for_kettle

    Output:
    {
        "step": 5,
        "action": "move_forward",
        "target": "kettle",
        "raw": "5_move_forward_for_kettle"
    }
    """
    if "_for_" not in folder_name:
        return None

    left, target = folder_name.split("_for_", 1)

    if "_" not in left:
        return None

    step_str, action = left.split("_", 1)

    try:
        step = int(step_str)
    except ValueError:
        return None

    return {
        "step": step,
        "action": action,
        "target": target,
        "raw": folder_name,
    }


def action_sort_key(action_item):
    """
    Sort action folders by step number.

    If the same step number appears multiple times, put stop after movement/turning.
    Example:
    132_move_forward_for_coffee table
    132_stop_for_coffee table
    """
    parsed = action_item["parsed"]

    step = parsed["step"]
    action = parsed["action"]

    action_priority = {
        "move_forward": 0,
        "turn_left": 0,
        "turn_right": 0,
        "stop": 1,
    }

    return (
        step,
        action_priority.get(action, 9),
        parsed["raw"],
    )


def load_action_sequence(trial_dir):
    """
    Load all action-step folders from success/trial_1.
    """
    trial_dir = Path(trial_dir)

    if not trial_dir.exists():
        raise FileNotFoundError(f"Trial directory not found: {trial_dir}")

    action_items = []

    for p in trial_dir.iterdir():
        if not p.is_dir():
            continue

        parsed = parse_action_folder_name(p.name)

        if parsed is None:
            continue

        existing_images = []
        missing_images = []

        for image_name in REQUIRED_IMAGES:
            image_path = p / image_name

            if image_path.exists():
                existing_images.append(image_name)
            else:
                missing_images.append(image_name)

        action_items.append(
            {
                "folder": p.name,
                "path": str(p),
                "parsed": parsed,
                "existing_images": existing_images,
                "missing_images": missing_images,
            }
        )

    action_items = sorted(action_items, key=action_sort_key)

    return action_items


def find_duplicate_step_numbers(action_items):
    """
    Find step numbers that appear more than once.
    """
    groups = defaultdict(list)

    for item in action_items:
        step = item["parsed"]["step"]
        groups[step].append(item["folder"])

    duplicates = {
        step: folders
        for step, folders in groups.items()
        if len(folders) > 1
    }

    return duplicates


def count_missing_images(action_items):
    """
    Count all missing image files.
    """
    missing_records = []

    for item in action_items:
        for image_name in item["missing_images"]:
            missing_records.append(
                {
                    "folder": item["folder"],
                    "missing_image": image_name,
                }
            )

    return missing_records


def summarize_actions(action_items):
    """
    Create a simple action summary.
    """
    action_counts = defaultdict(int)
    target_counts = defaultdict(int)

    for item in action_items:
        action = item["parsed"]["action"]
        target = item["parsed"]["target"]

        action_counts[action] += 1
        target_counts[target] += 1

    return {
        "total_action_folders": len(action_items),
        "action_counts": dict(action_counts),
        "target_counts": dict(target_counts),
        "first_10": [
            item["folder"]
            for item in action_items[:10]
        ],
        "last_10": [
            item["folder"]
            for item in action_items[-10:]
        ],
    }