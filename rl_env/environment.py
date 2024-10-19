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
        map_file : str = None
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
        self.map = Map()
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
        num_features_per_tile = 3
        # TODO: check if observation space is correct
        self.observation_space = spaces.Dict(
            {
                "map": spaces.Box(
                    low=0,
                    high=1,
                    shape=(self.map.max_x_index, self.map.max_y_index, num_features_per_tile),
                    dtype=np.float32,
                ),
                "agents": spaces.Box(
                    low=0,
                    high=max(self.map.width, self.map.height),
                    shape=(self.num_agents, 3),  # Example: [x, y, state]
                    dtype=np.float32,
                ),
            }
        )

        for agent in self.agents:
            agent.reset(self.env_settings)

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
        observations = self._get_observation()

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

    def get_env_state(self):
        map_info = self.map.get_observation()

        agent_info = {}
        for agent in self.agents:
            info = agent.get_state_for_env_info()
            agent_info[agent.id] = info

        env_info = {"map_info": map_info, "agent_info": agent_info}
        return env_info

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

    def _get_observation(self) -> Dict[str, Any]:
        """
        Constructs the observation dictionary.

        Returns:
            observation (Dict[str, Any]): The current observation.
        """
        map_observation = self.map.get_observation()
        agent_observations = np.array(
            [agent.get_observation() for agent in self.agents]
        )
        observation = {"map": map_observation, "agents": agent_observations}
        return observation

    def capture_game_state_as_image(self):
        screen_capture = pygame.display.get_surface()
        return np.transpose(pygame.surfarray.array3d(screen_capture), axes=[1, 0, 2])
