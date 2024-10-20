from typing import Any, Dict, List, Optional, Tuple

import gymnasium as gym
import numpy as np
import pygame
from gymnasium.vector.utils import spaces

from agents.Sim_Agent import Agent
from map.sim_map import Map
from rl_env.actions import ActionManager


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


def capture_game_state_as_image():
    screen_capture = pygame.display.get_surface()
    return np.transpose(pygame.surfarray.array3d(screen_capture), axes=[1, 0, 2])


class MapEnvironment(gym.Env):
    """
    A reinforcement learning environment for a multi-agent 2D Gridworld.

    Attributes:
        env_settings (dict): Configuration settings for the environment.
        num_agents (int): Number of agents in the environment.
        render_mode (bool): Whether to render the environment.
        map (Map): The grid map of the environment.
        agents (List[Agent]): List of agents in the environment.
        action_manager (ActionManager): Manages the application of actions.
    """

    metadata = {"render.modes": ["human", "rgb_array"]}

    def __init__(
        self,
        env_settings: Any,
        num_agents: int,
        screen,
        render_mode: str = "rgb_array",
        game_type: str = "automated",
        map_file: str = None,
    ):
        super(MapEnvironment, self).__init__()

        if game_type == "human":
            self.render_mode = "human"
            self.player = True
        else:
            self.player = False

        self.env_settings = env_settings
        self.num_agents = num_agents
        self.render_mode = render_mode

        self.screen = screen

        # Initialize the map
        self.map = Map(self.screen.get_width())
        if map_file is None:
            self.map.create_map(self.env_settings)
        else:
            self.map.load_topography_resources(map_file, self.env_settings)

        # Initialize agents
        self.agents: List[Agent] = [Agent(i) for i in range(self.num_agents)]

        # Initialize action manager
        self.action_manager = ActionManager(self, self.env_settings)

        # Define action and observation spaces
        self.action_space = spaces.Tuple(
            [
                spaces.Dict(
                    {
                        "move": spaces.Discrete(
                            5
                        ),  # 0: No move, 1: Up, 2: Down, 3: Left, 4: Right
                    }
                )
                for _ in range(self.num_agents)
            ]
        )

        for agent in self.agents:
            agent.reset(self.env_settings)

    def define_observation_space(self):
        # Number of features per tile on the map (as per your 'get_full_info' method)
        num_features_per_tile = 5  # 'height', 'biome', 'resources', 'land_type', 'owner_value', 'land_money_value'

        # Define the minimum and maximum values for each map feature
        # Replace these with the actual min and max values appropriate for your environment
        min_height = 0.0
        max_height = 100.0

        min_biome = 0  # Assuming biome is an integer code (e.g., 0 to 10)
        max_biome = 10

        # min_resources = 0.0
        # max_resources = 1000.0

        min_land_type = 0  # Assuming land_type is an integer code (e.g., 0 to 5)
        max_land_type = 5

        min_owner_value = (
            0  # Assuming owner_value is an integer (e.g., agent ID starting from 0)
        )
        max_owner_value = (
            self.num_agents - 1
        )  # Agent IDs range from 0 to num_agents - 1

        min_land_money_value = 0.0
        max_land_money_value = 10000.0

        # Create arrays for the minimum and maximum values of the map features
        map_feature_mins = np.array(
            [
                min_height,
                min_biome,
                # min_resources,
                min_land_type,
                min_owner_value,
                min_land_money_value,
            ],
            dtype=np.float32,
        )

        map_feature_maxs = np.array(
            [
                max_height,
                max_biome,
                # max_resources,
                max_land_type,
                max_owner_value,
                max_land_money_value,
            ],
            dtype=np.float32,
        )

        # Create the low and high arrays for the map observation space
        # These arrays have the shape (map_width, map_height, num_features_per_tile)
        map_low = (
            np.zeros(
                (self.map.width, self.map.height, num_features_per_tile),
                dtype=np.float32,
            )
            + map_feature_mins
        )
        map_high = (
            np.zeros(
                (self.map.width, self.map.height, num_features_per_tile),
                dtype=np.float32,
            )
            + map_feature_maxs
        )

        # Define the map observation space
        map_observation_space = spaces.Box(low=map_low, high=map_high, dtype=np.float32)

        # Number of features per agent ('state' and 'money')
        num_agent_features = 2

        # Define the minimum and maximum values for each agent feature
        # Replace these with the actual min and max values appropriate for your environment
        state_min = 0.0
        state_max = 1.0

        money_min = 0.0
        money_max = 1000.0

        # Create arrays for the minimum and maximum values of the agent features
        agent_feature_mins = np.array([state_min, money_min], dtype=np.float32)
        agent_feature_maxs = np.array([state_max, money_max], dtype=np.float32)

        # Define the agents' observation space
        agents_observation_space = spaces.Box(
            low=agent_feature_mins,
            high=agent_feature_maxs,
            shape=(self.num_agents, num_agent_features),
            dtype=np.float32,
        )

        # Define the overall observation space using spaces.Dict
        self.observation_space = spaces.Dict(
            {"map": map_observation_space, "agents": agents_observation_space}
        )

    def reset(self) -> Dict[str, Any]:
        """
        Resets the environment to an initial state and returns an initial observation.

        Returns:
            observation (Dict[str, Any]): The initial observation of the environment.
        """
        self.map.reset()
        for agent in self.agents:
            agent.reset(self.env_settings)

        return self._get_observation()

    def step(
        self, actions: Any
    ) -> Tuple[dict[str, Any], List[float], List[bool], Dict]:
        """
        Executes the actions for all agents and updates the environment state.

        Args:
            actions (List[Dict[str, int]]): A list of action dictionaries for each agent.
        """
        info = {}

        # Apply actions using ActionManager
        rewards, dones = self.action_manager.apply_actions(actions, self.agents)

        # Update environment state
        self._update_environment_state()

        # Collect observations
        observations = self.get_observation()

        return observations, rewards, dones, info

    def render(self) -> Optional[np.ndarray]:
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
                agent.draw(self.screen, self.map.tile_size, 0, 0, 0)
            # Update the display
            pygame.display.flip()

        elif self.render_mode == "rgb_array":
            # Return an RGB array of the current frame
            screen_capture = self.capture_game_state_as_image()
            return screen_capture
        else:
            raise NotImplementedError("Unknown ender mode !!")

    def get_possible_actions(self, agent_id):
        possible_actions = []
        agent = self.agents[agent_id]
        possible_actions.append(agent.get_possible_actions())

        return possible_actions

    def _update_environment_state(self):
        """
        Updates the environment state after actions have been applied.
        """
        # Update map dynamics if any
        # self.map.update()
        # Update agents
        for agent in self.agents:
            agent.update()

    def get_observation(self) -> Dict[str, Any]:
        """
        Constructs the observation dictionary.

        Returns:
            observation (Dict[str, Any]): The current observation.
        """
        map_observation = self.map.get_observation()
        agent_observations = np.array(
            [agent.get_observation() for agent in self.agents],
            dtype=np.float32,
        )
        observation = {"map": map_observation, "agents": agent_observations}
        return observation

    def capture_game_state_as_image(self):
        screen_capture = pygame.display.get_surface()
        return np.transpose(pygame.surfarray.array3d(screen_capture), axes=[1, 0, 2])
