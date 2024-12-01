from typing import Any, Dict, List, Optional

import gymnasium as gym
import numpy as np
import pygame
from gymnasium import spaces

from rl_env.ActionManager import ActionManager
from rl_env.map.sim_map import Map
from rl_env.Sim_Agent import Agent


def check_done(agent):
    if agent.state == "Done":
        return True
    else:
        return False


def calculate_reward(agent):
    if check_done(agent):
        return agent.money + 1000
    else:
        return agent.money


def setup_screen(render_mode: str):
    if render_mode != "human":
        return

    screen = pygame.display.set_mode((default_screen_size_x, default_screen_size_y))
    pygame.display.set_caption("Agent-based Strategy RL")
    screen.fill((0, 0, 0))  # Fill the screen with black color
    return screen


def capture_game_state_as_image():
    screen_capture = pygame.display.get_surface()
    return np.transpose(pygame.surfarray.array3d(screen_capture), axes=[1, 0, 2])


default_screen_size_x = 1000
default_screen_size_y = 1000


class MapEnvironment(gym.Env):
    """
    A reinforcement learning environment for a multi-agent 2D Gridworld.

    Attributes:
        env_settings (Dict[str, Any]): A dictionary containing environment settings.
        num_agents (int): The number of agents in the environment.
        render_mode (str): The mode to render with. Options are 'human' or 'rgb_array'.
        seed (Optional[int]): The seed for the environment's random number generator.
    """

    metadata = {"render.modes": ["human", "rgb_array"]}

    def __init__(
        self,
        env_settings: Any,
        num_agents: int,
        render_mode: str = "rgb_array",
        seed: Optional[int] = None,
    ):
        super(MapEnvironment, self).__init__()

        self.env_settings = env_settings

        self.num_agents = num_agents
        self.render_mode = render_mode

        self.screen = setup_screen(self.render_mode)

        # Initialize the map
        self.map = Map(self)

        # Initialize agents
        self.agents: List[Agent] = [Agent(i, self) for i in range(self.num_agents)]

        # Initialize action manager
        self.action_manager = ActionManager(self)
        self.action_mapping = None

        # Define action and observation spaces
        self.observation_space = self._define_observation_space()
        self.action_space = self._define_action_space()

        for agent in self.agents:
            agent.reset()

    def reset(self, seed=None):
        """
        Resets the environment to an initial state and returns an initial observation.
        """
        super().reset(seed=seed)
        self.map.reset()
        for agent in self.agents:
            agent.reset()
        observations = self._get_observation()
        info = {"info": "no info here"}
        return observations, info

    def step(self, actions: Any):
        """
        Executes the actions for all agents and updates the environment state.

        Args:
            actions (List[Dict[str, int]]): A list of action dictionaries for each agent.
        """
        info = {}

        rewards, dones = self.action_manager.apply_actions(actions)

        self._update_environment_state()

        observations = self._get_observation()

        truncated = False
        return observations, rewards, False, truncated, info

    def render(self):
        """
        Renders the environment.

        Args:
            mode (str): The mode to render with. Options are 'human' or 'rgb_array'.

        Returns:
            Optional[np.ndarray]: The rendered image array if mode is 'rgb_array', else None.
        """

        if self.render_mode == "human":
            # Implement rendering logic using Pygame or another library
            self.map.draw(self.screen, 1, 0, 0)
            for agent in self.agents:
                agent.draw(self.map.tile_size, 0, 0, 0)
            # Update the display
            pygame.display.flip()

        elif self.render_mode == "rgb_array":
            # Return an RGB array of the current frame
            screen_capture = capture_game_state_as_image()
            return screen_capture
        else:
            raise NotImplementedError("Unknown render mode !!")

    def close(self):
        """
        Closes the environment.
        """
        pygame.quit()

    def _define_observation_space(self):
        data = self.env_settings["map_features"]
        selected_features = [
            feature for feature in data if feature.get("select", False)
        ]
        self.features_per_tile = selected_features

        data = self.env_settings["agent_features"]
        selected_features = [
            feature for feature in data if feature.get("select", False)
        ]
        self.agent_features = selected_features

        # map observation space
        map_feature_mins = np.zeros(len(self.features_per_tile), dtype=np.float32)
        map_feature_maxs = np.zeros(len(self.features_per_tile), dtype=np.float32)

        i = 0
        for feature in self.features_per_tile:
            map_feature_mins[i] = float(feature["values"]["min"])
            map_feature_maxs[i] = float(feature["values"]["max"])
            i += 1

        map_low = (
            np.zeros(
                (self.map.width, self.map.height, len(self.features_per_tile)),
                dtype=np.float32,
            )
            + map_feature_mins
        )
        map_high = (
            np.zeros(
                (self.map.width, self.map.height, len(self.features_per_tile)),
                dtype=np.float32,
            )
            + map_feature_maxs
        )
        map_observation_space = spaces.Box(low=map_low, high=map_high, dtype=np.float32)

        # agent observation space
        agent_feature_mins = np.zeros(len(self.agent_features), dtype=np.float32)
        agent_feature_maxs = np.zeros(len(self.agent_features), dtype=np.float32)

        i = 0
        for feature in self.agent_features:
            agent_feature_mins[i] = float(feature["values"]["min"])
            agent_feature_maxs[i] = float(feature["values"]["max"])
            i += 1

        agent_low = (
            np.zeros(
                (self.num_agents, len(self.agent_features)),
                dtype=np.float32,
            )
            + agent_feature_mins
        )
        agent_high = (
            np.zeros(
                (self.num_agents, len(self.agent_features)),
                dtype=np.float32,
            )
            + agent_feature_maxs
        )

        agents_observation_space = spaces.Box(
            low=agent_low,
            high=agent_high,
            shape=(self.num_agents, len(self.agent_features)),
            dtype=np.float32,
        )

        return spaces.Dict(
            {"map": map_observation_space, "agents": agents_observation_space}
        )

    def _define_action_space(self):
        actions = self.env_settings["actions"]

        enabled_actions = []

        for action_name, action_properties in actions.items():
            # Check if the action is enabled (cost is not -1)
            if action_properties.get("cost", -1) >= 0:
                enabled_actions.append(action_name)

        num_action_types = len(enabled_actions)
        grid_width = self.map.width
        grid_height = self.map.height

        self.action_mapping = {
            i: action_name for i, action_name in enumerate(enabled_actions)
        }
        action_space = spaces.MultiDiscrete([num_action_types, grid_width, grid_height])

        return action_space

    def _update_environment_state(self):
        """
        Updates the environment state after actions have been applied.A
        """
        # Update map dynamics if any
        # self.map.update()

        for agent in self.agents:
            agent.update()

    def _get_observation(self):
        """
        Constructs the observation dictionary.

        Returns:
            observation (Dict[str, Any]): The current observation.
        """

        # all_visible_masks = []
        # for agent in self.agents:
        #     all_visible_masks.append(get_visible_mask(agent.id, self.map))

        map_observation = self.map.get_observation()
        agent_observations = np.zeros(
            (self.num_agents, len(self.agent_features)), dtype=np.float32
        )

        for i, agent in enumerate(self.agents):
            agent_observations[i] = agent.get_observation()

        # np_all_visible_masks = np.array(all_visible_masks)
        # agent_info = np.array([])

        return {"map": map_observation, "agents": agent_observations}
