import json
from pathlib import Path


def load_json(path):
    """
    Load a JSON file.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_lhpr_task(task_cfg):
    """
    Load one LHPR-VLN task using the task YAML config.
    """
    task_dir = Path(task_cfg["task_dir"])
    trial_dir = task_dir / task_cfg["replay"]["trial_folder"]

    config_json_path = task_dir / "config.json"
    task_json_path = trial_dir / "task.json"

    task_config = load_json(config_json_path)
    task_json = load_json(task_json_path)

    step_task_json_paths = sorted(
        [
            p for p in trial_dir.glob("*.json")
            if p.name != "task.json"
        ]
    )

    step_tasks = []

    for p in step_task_json_paths:
        data = load_json(p)

        step_tasks.append(
            {
                "file_name": p.name,
                "path": str(p),
                "trajectory_path": data.get("trajectory path"),
                "start": data.get("start"),
                "end": data.get("end"),
                "robot": data.get("Robot"),
                "scene": data.get("Scene"),
                "target": data.get("target"),
                "region": data.get("Region"),
                "start_pos": data.get("start_pos"),
                "start_yaw": data.get("start_yaw"),
                "instruction": data.get("Task instruction"),
            }
        )

    subtask_list = task_config.get("Subtask list", [])
    expected_move_to_count = sum(
        1 for s in subtask_list
        if isinstance(s, str) and s.startswith("Move_to")
    )

    return {
        "task_dir": str(task_dir),
        "trial_dir": str(trial_dir),
        "config_json_path": str(config_json_path),
        "task_json_path": str(task_json_path),
        "task_config": task_config,
        "task_json": task_json,
        "step_tasks": step_tasks,
        "expected_move_to_count": expected_move_to_count,
    }


def summarize_task(task_bundle):
    """
    Create a simple printable summary of the loaded task.
    """
    cfg = task_bundle["task_config"]

    return {
        "instruction": cfg.get("Task instruction"),
        "robot": cfg.get("Robot"),
        "scene": cfg.get("Scene"),
        "start_pos": cfg.get("Start pos"),
        "objects": cfg.get("Object"),
        "subtask_list": cfg.get("Subtask list", []),
        "expected_move_to_count": task_bundle["expected_move_to_count"],
        "actual_step_task_json_count": len(task_bundle["step_tasks"]),
    }