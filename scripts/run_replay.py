import argparse

from lhpr_vln.config import load_all_configs
from lhpr_vln.task_loader import load_lhpr_task
from lhpr_vln.action_loader import load_action_sequence
from lhpr_vln.habitat_replay import (
    create_simulator,
    set_agent_start_state,
    replay_actions,
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

    task_cfg = configs["task"]
    sim_cfg = configs["simulator"]

    print("=" * 100)
    print("LHPR-VLN HABITAT REPLAY")
    print("=" * 100)

    print("\nInstruction:")
    print(task_cfg["instruction"])

    print("\nScene:")
    print(task_cfg["scene"]["scene_id"])

    print("\nGLB:")
    print(task_cfg["scene"]["glb"])

    print("\nNavmesh:")
    print(task_cfg["scene"]["navmesh"])

    print("\nStart:")
    print("Position:", task_cfg["start"]["position"])
    print("Yaw:", task_cfg["start"]["yaw"])

    task_bundle = load_lhpr_task(task_cfg)
    action_items = load_action_sequence(task_bundle["trial_dir"])

    print("\nLoaded action folders:", len(action_items))

    sim = create_simulator(task_cfg, sim_cfg)
    set_agent_start_state(sim, task_cfg)

    try:
        replay_actions(sim, task_cfg, sim_cfg, action_items)
    finally:
        sim.close()


if __name__ == "__main__":
    main()
