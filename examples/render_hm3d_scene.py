import os
import math
import numpy as np
from PIL import Image

import habitat_sim
from habitat_sim.utils.common import quat_from_angle_axis


# Default scene path
DEFAULT_SCENE = "data/scene_datasets/hm3d/val/00887-hyFzGGJCSYs/hyFzGGJCSYs.basis.glb"

# Use terminal SCENE variable if provided, otherwise use DEFAULT_SCENE
scene_path = os.environ.get("SCENE", DEFAULT_SCENE)

if not os.path.exists(scene_path):
    raise FileNotFoundError(f"Scene file not found: {scene_path}")

print(f"Loading scene: {scene_path}")

output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

# Simulator config
sim_cfg = habitat_sim.SimulatorConfiguration()
sim_cfg.scene_id = scene_path
sim_cfg.enable_physics = False

# RGB camera config
rgb_sensor = habitat_sim.CameraSensorSpec()
rgb_sensor.uuid = "color_sensor"
rgb_sensor.sensor_type = habitat_sim.SensorType.COLOR
rgb_sensor.resolution = [512, 512]
rgb_sensor.position = [0.0, 1.5, 0.0]  # camera height

# Agent config
agent_cfg = habitat_sim.agent.AgentConfiguration()
agent_cfg.sensor_specifications = [rgb_sensor]

# Start simulator
cfg = habitat_sim.Configuration(sim_cfg, [agent_cfg])
sim = habitat_sim.Simulator(cfg)

agent = sim.initialize_agent(0)

# Render 5 random views
for i in range(5):
    position = sim.pathfinder.get_random_navigable_point()

    state = agent.get_state()
    state.position = position

    yaw = np.random.uniform(0, 2 * math.pi)
    state.rotation = quat_from_angle_axis(yaw, np.array([0, 1, 0]))

    agent.set_state(state)

    observations = sim.get_sensor_observations()
    rgb = observations["color_sensor"][:, :, :3]

    out_path = os.path.join(output_dir, f"hm3d_view_{i}.png")
    Image.fromarray(rgb).save(out_path)

    print(f"Saved: {out_path}")

sim.close()