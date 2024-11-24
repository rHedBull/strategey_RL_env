from typing import Any, Dict, List, Optional, Tuple

import gymnasium as gym
import numpy as np
import pygame
from gymnasium import spaces

from agents.Sim_Agent import Agent, get_visible_mask
from map.sim_map import Map
from rl_env.ActionManager import ActionManager


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

        # Define action and observation spaces
        self.observation_space = None # TODO: do this
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
            agent.reset()


    def reset(self, seed=None):
        """
        Resets the environment to an initial state and returns an initial observation.
        """
        super().reset(seed=seed)
        self.map.reset()
        for agent in self.agents:
            agent.reset()
        map_obs, agent_info, visibility_masks = self._get_observation()
        info = {"info": "no info here"}
        return map_obs, agent_info, visibility_masks, info

    def step(
        self, actions: Any
    ):
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
        map_obs, agent_info, visibility_masks = self._get_observation()

        return map_obs, rewards, dones, info

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
                agent.draw(self.map.tile_size, 0, 0,0)
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

    def _seed(self, seed=None) -> None:
        """
        Sets the seed for the environment's random number generator.
        """
        self.np_random = np.random.RandomState(seed)

    def _define_observation_space(self):
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


    def _update_environment_state(self):
        """
        Updates the environment state after actions have been applied.A
        """
        # Update map dynamics if any
        # self.map.update()
        # Update agents
        for agent in self.agents:
            agent.update()

    def _get_observation(self) -> Dict[str, Any]:
        """
        Constructs the observation dictionary.

        Returns:
            observation (Dict[str, Any]): The current observation.
        """

        all_visible_masks = []
        for agent in self.agents:
            all_visible_masks.append(get_visible_mask(agent.id, self.map))

        map_observation = self.map.get_observation()
        # agent_observations = np.array(
        #     [agent.get_observation() for agent in self.agents],
        #     dtype=np.float32,
        # )

        np_all_visible_masks = np.array(all_visible_masks)
        agent_info = np.array([])

        return map_observation, agent_info, np_all_visible_masks
