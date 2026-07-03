import time

import cv2
import numpy as np
from habitat_sim.utils.common import quat_from_angle_axis

from lhpr_vln.habitat_replay import (
    add_overlay,
    create_simulator,
    render_observation,
)


def set_agent_pose(sim, position, yaw_deg):
    """
    Set Habitat agent state directly from an LHPR position and yaw.
    """
    agent = sim.get_agent(0)
    state = agent.get_state()

    state.position = np.array(position, dtype=np.float32)

    yaw_rad = np.deg2rad(float(yaw_deg))
    state.rotation = quat_from_angle_axis(yaw_rad, np.array([0.0, 1.0, 0.0]))

    agent.set_state(state)


def get_corrected_yaw(raw_yaw, task_cfg):
    """
    Apply pose replay yaw convention settings from the task YAML.
    """
    pose_replay_cfg = task_cfg.get("pose_replay", {})
    yaw_sign = float(pose_replay_cfg.get("yaw_sign", 1.0))
    yaw_offset = float(pose_replay_cfg.get("yaw_offset", 0.0))

    return float(raw_yaw) * yaw_sign + yaw_offset


def add_pose_overlay(frame, item, index, total, instruction):
    """
    Reuse the action overlay with pose-specific index information.
    """
    action_item = item["action_folder"]
    frame = add_overlay(frame, action_item, index, total, instruction)

    pose = item["pose"]
    line = (
        f"Pose {pose['global_index']} | "
        f"{pose['source_trial']}[{pose['local_index']}] | "
        f"Yaw: {pose['yaw']} -> {item['corrected_yaw']}"
    )

    cv2.putText(
        frame,
        line,
        (20, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    return frame


def replay_poses(task_cfg, sim_cfg, paired_items):
    """
    Replay saved LHPR task.json poses inside Habitat.
    """
    sim = create_simulator(task_cfg, sim_cfg)

    sensor_uuid = sim_cfg["sensor"]["rgb"]["uuid"]
    viewer_cfg = sim_cfg["viewer"]

    window_name = viewer_cfg.get("window_name", "LHPR-VLN Pose Replay")
    fps = float(viewer_cfg.get("fps", 5))
    show_text_overlay = bool(viewer_cfg.get("show_text_overlay", True))
    delay_ms = int(1000 / fps)

    instruction = task_cfg["instruction"]

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    print("\nPose replay controls:")
    print("  q = quit")
    print("  space = pause/continue")
    print("\nStarting pose-based Habitat replay...\n")

    paused = False

    try:
        for i, item in enumerate(paired_items):
            pose = item["pose"]
            corrected_yaw = get_corrected_yaw(pose["yaw"], task_cfg)

            item["corrected_yaw"] = corrected_yaw
            set_agent_pose(sim, pose["pos"], corrected_yaw)
            frame = render_observation(sim, sensor_uuid)

            if show_text_overlay:
                frame = add_pose_overlay(
                    frame,
                    item,
                    i,
                    len(paired_items),
                    instruction,
                )

            cv2.imshow(window_name, frame)

            key = cv2.waitKey(delay_ms) & 0xFF

            if key == ord("q"):
                break

            if key == ord(" "):
                paused = not paused

            while paused:
                key = cv2.waitKey(100) & 0xFF

                if key == ord(" "):
                    paused = False

                if key == ord("q"):
                    return

            time.sleep(0.001)

        print("\nPose replay finished.")
    finally:
        cv2.destroyAllWindows()
        sim.close()
