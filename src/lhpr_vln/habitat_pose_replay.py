import time

import cv2
import numpy as np
from habitat_sim.utils.common import quat_from_angle_axis

from lhpr_vln.habitat_replay import create_simulator


def set_agent_pose(agent, pos, yaw_degrees, yaw_sign=1.0, yaw_offset=0.0):
    """
    Directly set Habitat agent position and yaw.
    """
    state = agent.get_state()

    state.position = np.array(pos, dtype=np.float32)

    corrected_yaw = (float(yaw_degrees) * float(yaw_sign)) + float(yaw_offset)
    yaw_rad = np.deg2rad(corrected_yaw)

    state.rotation = quat_from_angle_axis(
        yaw_rad,
        np.array([0.0, 1.0, 0.0])
    )

    agent.set_state(state, reset_sensors=True)


def render_current_frame(sim, sensor_uuid):
    obs = sim.get_sensor_observations()
    rgb = obs[sensor_uuid]

    if rgb.shape[-1] == 4:
        rgb = rgb[:, :, :3]

    frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    return frame


def add_pose_overlay(frame, pair, total, instruction):
    pose = pair["pose"]
    action_folder = pair["action_folder"]
    parsed = action_folder["parsed"]

    step = parsed["step"]
    target = parsed["target"]
    action_folder_action = parsed["action"]

    action_json = pose["action_from_task_json"]
    yaw = pose["yaw"]
    trial = pose["source_trial"]

    line1 = f"Step {step} | Folder action: {action_folder_action} | JSON action: {action_json}"
    line2 = f"Target: {target} | Yaw: {yaw} | {trial} | {pair['index'] + 1}/{total}"
    line3 = instruction[:95]

    cv2.putText(
        frame,
        line1,
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        line2,
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.60,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        line3,
        (20, frame.shape[0] - 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    return frame


def replay_poses(task_cfg, sim_cfg, paired_items):
    """
    Pose-based replay:
    directly sets agent position and yaw from task.json.
    """
    sim = create_simulator(task_cfg, sim_cfg)
    agent = sim.initialize_agent(0)

    sensor_uuid = sim_cfg["sensor"]["rgb"]["uuid"]
    viewer_cfg = sim_cfg["viewer"]

    window_name = viewer_cfg.get("window_name", "LHPR-VLN Pose Replay")
    fps = float(viewer_cfg.get("fps", 5))
    show_text_overlay = bool(viewer_cfg.get("show_text_overlay", True))

    pose_replay_cfg = task_cfg.get("pose_replay", {})
    yaw_sign = pose_replay_cfg.get("yaw_sign", 1.0)
    yaw_offset = pose_replay_cfg.get("yaw_offset", 0.0)

    delay_ms = int(1000 / fps)

    instruction = task_cfg["instruction"]

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    print("\nPose replay controls:")
    print("  q = quit")
    print("  space = pause/continue")
    print("\nStarting pose-based Habitat replay...\n")

    paused = False

    try:
        for pair in paired_items:
            pose = pair["pose"]

            set_agent_pose(
                agent=agent,
                pos=pose["pos"],
                yaw_degrees=pose["yaw"],
                yaw_sign=yaw_sign,
                yaw_offset=yaw_offset,
            )

            frame = render_current_frame(sim, sensor_uuid)

            if show_text_overlay:
                frame = add_pose_overlay(
                    frame,
                    pair,
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
                    cv2.destroyAllWindows()
                    return

            time.sleep(0.001)

    finally:
        cv2.destroyAllWindows()
        sim.close()

    print("\nPose replay finished.")
