from pathlib import Path
import time

import cv2
import numpy as np
import habitat_sim
from habitat_sim.agent import AgentConfiguration, ActionSpec, ActuationSpec
from habitat_sim.utils.common import quat_from_angle_axis


VALID_HABITAT_ACTIONS = {"move_forward", "turn_left", "turn_right"}


def create_simulator(task_cfg, sim_cfg):
    """
    Create Habitat-Sim simulator using scene and simulator YAML configs.
    """
    scene_glb = Path(task_cfg["scene"]["glb"])
    navmesh = Path(task_cfg["scene"]["navmesh"])

    if not scene_glb.exists():
        raise FileNotFoundError(f"Scene GLB not found: {scene_glb}")

    if not navmesh.exists():
        raise FileNotFoundError(f"Navmesh not found: {navmesh}")

    rgb_cfg = sim_cfg["sensor"]["rgb"]

    sim_settings = habitat_sim.SimulatorConfiguration()
    sim_settings.scene_id = str(scene_glb)

    rgb_sensor = habitat_sim.CameraSensorSpec()
    rgb_sensor.uuid = rgb_cfg["uuid"]
    rgb_sensor.sensor_type = habitat_sim.SensorType.COLOR
    rgb_sensor.resolution = [rgb_cfg["height"], rgb_cfg["width"]]
    rgb_sensor.position = rgb_cfg["position"]

    agent_cfg = AgentConfiguration()
    agent_cfg.sensor_specifications = [rgb_sensor]

    agent_cfg.action_space = {
        "move_forward": ActionSpec(
            "move_forward",
            ActuationSpec(amount=sim_cfg["actions"]["move_forward"]["amount"]),
        ),
        "turn_left": ActionSpec(
            "turn_left",
            ActuationSpec(amount=sim_cfg["actions"]["turn_left"]["amount"]),
        ),
        "turn_right": ActionSpec(
            "turn_right",
            ActuationSpec(amount=sim_cfg["actions"]["turn_right"]["amount"]),
        ),
    }

    habitat_cfg = habitat_sim.Configuration(sim_settings, [agent_cfg])
    sim = habitat_sim.Simulator(habitat_cfg)

    sim.pathfinder.load_nav_mesh(str(navmesh))

    return sim


def set_agent_start_state(sim, task_cfg):
    """
    Set initial position and yaw from task YAML.
    """
    agent = sim.initialize_agent(0)
    state = agent.get_state()

    start_position = np.array(task_cfg["start"]["position"], dtype=np.float32)
    start_yaw_deg = float(task_cfg["start"]["yaw"])

    state.position = start_position

    yaw_rad = np.deg2rad(start_yaw_deg)
    state.rotation = quat_from_angle_axis(yaw_rad, np.array([0.0, 1.0, 0.0]))

    agent.set_state(state)

    return agent


def should_skip_action(item, task_cfg):
    """
    Decide whether an action should be skipped based on replay YAML settings.
    """
    parsed = item["parsed"]
    action = parsed["action"]
    step = parsed["step"]

    replay_cfg = task_cfg["replay"]

    if replay_cfg.get("skip_initial_stop", False):
        if step == -1 and action == "stop":
            return True

    if replay_cfg.get("skip_stop_actions", False):
        if action == "stop":
            return True

    return False


def render_observation(sim, sensor_uuid):
    """
    Get current RGB frame from Habitat-Sim.
    """
    obs = sim.get_sensor_observations()
    rgb = obs[sensor_uuid]

    if rgb.shape[-1] == 4:
        rgb = rgb[:, :, :3]

    frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    return frame


def add_overlay(frame, item, index, total, instruction):
    """
    Add text overlay to viewer frame.
    """
    parsed = item["parsed"]

    step = parsed["step"]
    action = parsed["action"]
    target = parsed["target"]

    line1 = f"Step {step} | Action: {action} | Target: {target}"
    line2 = f"{index + 1}/{total}"
    line3 = instruction[:95]

    cv2.putText(
        frame,
        line1,
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        line2,
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
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


def replay_actions(sim, task_cfg, sim_cfg, action_items):
    """
    Replay sorted action folders inside Habitat viewer.
    """
    sensor_uuid = sim_cfg["sensor"]["rgb"]["uuid"]
    viewer_cfg = sim_cfg["viewer"]

    window_name = viewer_cfg.get("window_name", "LHPR-VLN Habitat Replay")
    fps = float(viewer_cfg.get("fps", 5))
    show_text_overlay = bool(viewer_cfg.get("show_text_overlay", True))

    delay_ms = int(1000 / fps)

    instruction = task_cfg["instruction"]

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    print("\nReplay controls:")
    print("  q = quit")
    print("  space = pause/continue")
    print("\nStarting Habitat replay...\n")

    paused = False

    for i, item in enumerate(action_items):
        if should_skip_action(item, task_cfg):
            continue

        parsed = item["parsed"]
        action = parsed["action"]

        if action in VALID_HABITAT_ACTIONS:
            obs = sim.step(action)
            rgb = obs[sensor_uuid]

            if rgb.shape[-1] == 4:
                rgb = rgb[:, :, :3]

            frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        elif action == "stop":
            frame = render_observation(sim, sensor_uuid)

        else:
            print(f"Skipping unknown action: {action}")
            frame = render_observation(sim, sensor_uuid)

        if show_text_overlay:
            frame = add_overlay(frame, item, i, len(action_items), instruction)

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

    print("\nReplay finished.")
    cv2.destroyAllWindows()
