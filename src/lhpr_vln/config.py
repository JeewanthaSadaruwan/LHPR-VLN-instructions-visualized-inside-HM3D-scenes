from pathlib import Path
from typing import Union

import yaml


def load_yaml(path: Union[str, Path]) -> dict:
    """
    Load one YAML config file.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        raise ValueError(f"YAML file is empty: {path}")

    return data


def resolve_path(path_str: str, project_root: Union[str, Path] = ".") -> Path:
    """
    Convert a relative path from YAML into a real Path object.
    """
    path = Path(path_str)

    if path.is_absolute():
        return path

    return Path(project_root) / path


def load_all_configs(paths_yaml: str, sim_yaml: str, task_yaml: str) -> dict:
    """
    Load paths, simulator, and replay-task configs together.
    """
    paths_cfg = load_yaml(paths_yaml)
    sim_cfg = load_yaml(sim_yaml)
    task_cfg = load_yaml(task_yaml)

    project_root = Path(paths_cfg.get("project_root", "."))

    return {
        "project_root": project_root,
        "paths": paths_cfg,
        "simulator": sim_cfg,
        "task": task_cfg,
    }


def check_required_paths(configs: dict) -> dict:
    """
    Check whether the required task and scene paths exist.
    """
    project_root = configs["project_root"]
    task_cfg = configs["task"]

    task_dir = resolve_path(task_cfg["task_dir"], project_root)
    scene_glb = resolve_path(task_cfg["scene"]["glb"], project_root)
    navmesh = resolve_path(task_cfg["scene"]["navmesh"], project_root)

    trial_dir = task_dir / task_cfg["replay"]["trial_folder"]
    config_json = task_dir / "config.json"
    task_json = trial_dir / "task.json"

    checks = {
        "task_dir": task_dir,
        "config_json": config_json,
        "trial_dir": trial_dir,
        "task_json": task_json,
        "scene_glb": scene_glb,
        "navmesh": navmesh,
    }

    return checks
