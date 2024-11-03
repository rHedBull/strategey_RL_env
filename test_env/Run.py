import uuid
from datetime import datetime
from typing import Any

import numpy as np
import pygame
import tensorflow as tf

from rl_env.environment import capture_game_state_as_image
from test_env.Agent import Agent
from test_env.Player import Player


class Run:
    def __init__(self, settings_file, hyperparameters, env):
        self.id = uuid.uuid4()
        self.settings = settings_file

        self.hyper_settings = hyperparameters
        self.max_steps = self.settings.get_setting("max_steps")
        self.num_agents = self.settings.get_setting("num_agents")
        self.agents = []
        self.env = env

        current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_dir = "test_env/logs/agent_performance/" + current_time
        self.summary_writer = tf.summary.create_file_writer(log_dir)

    def run(self):
        pygame.init()

        self.setup_agents()

        # run the game loop
        step = 0
        # list of agents that are still running, by index in agents list
        running_agents = [i for i in range(self.num_agents)]
        all_done = False

        observation = self.env.get_observation()

        while not all_done and step < self.max_steps:
            self.env.render()  # checks already if rendering is on

            # get actions from agents
            agent_actions = []

            for agent in self.agents:
                if agent.state == "Done":
                    agent_actions.append(-1)
                    continue
                # if agent is a player, get action from keyboard
                if isinstance(agent, Player):
                    action = agent.get_action(pygame, None)

                else:
                    agent_observation = mask_map_for_agent(observation, agent.id)
                    action = agent.get_action(agent_observation)

                agent_actions.append(action)

            observation, agent_rewards, dones, all_done = self.env.step(agent_actions)

            self.update_agents(all_done, running_agents, dones, agent_rewards)
            self.log_stats(agent_rewards, step, agent_actions)

            self.check_if_all_done(dones)
            step += 1

        self.close()

    def log_stats(self, reward, step, actions):
        if step % self.settings.get_setting("storing_round_interval") == 0:
            with self.summary_writer.as_default():
                for i, _ in enumerate(self.agents):
                    tf.summary.scalar("reward_agent_{}".format(i), reward[i], step)
                    # tf.summary.scalar("action_agent_{}".format(i), actions[i], step) # TODO: reenable this

        if step % self.settings.get_setting("image_logging_round_interval") == 0:
            game_state_image = capture_game_state_as_image()
            tensor_img = tf.convert_to_tensor(game_state_image, dtype=tf.uint8)
            tensor_img = tf.expand_dims(tensor_img, 0)  # Add the batch dimension
            with self.summary_writer.as_default():
                tf.summary.image("Step: " + str(step), tensor_img, step)

    def update_agents(self, all_done, running_agents, dones, rewards):
        for i, done, reward in zip(running_agents, dones, rewards):
            if done:
                if isinstance(self.agents[i], Player):
                    print("Player {} is done".format(i))
                else:
                    print("Agent {} is done".format(i))
                self.agents[i].state = "Done"
            self.agents[i].update(reward)

        running_agents = [
            agent for agent, done in zip(running_agents, dones) if not done
        ]

        # check if the game is over
        # if all_done:
        #     print("game done")

    def setup_agents(self):
        if self.env.player:
            self.agents = [Player(0, self.env.map.width, self.env.map.height)]
            for i in range(1, self.num_agents):
                agent = Agent(i, self.env.map.width, self.env.map.height)
                self.agents.append(agent)
        else:
            for i in range(self.num_agents):
                agent = Agent(i, self.env.map.width, self.env.map.height)
                self.agents.append(agent)

    def check_if_all_done(self, dones):
        # check if all in dones are true

        for i in dones:
            if not i:
                return False

        self.close()
        return True

    def close(self):
        print("Game Terminated")
        if self.env.render_mode:
            if self.env.player:
                print("Press q to close the window")
                # keep the window open until the user closes it manually
                running = True
                while running:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            keys = pygame.key.get_pressed()
                            if keys[pygame.K_q]:
                                running = False

            pygame.quit()
        else:
            pygame.quit()


def mask_map_for_agent(
    observation: dict, agent_id: int, mask_value: int = -1
) -> list[tuple[Any, Any]] | Any:
    """
    Masks the map for a specific agent by setting all unseen tiles to mask_value.

    Args:
        observation (dict): The observation containing 'map' and 'visibility_masks'.
        agent_id (int): The ID of the agent.
        mask_value (int, optional): The value to set for unseen tiles. Defaults to -1.

    Returns:
        np.ndarray: The masked map observation for the agent.
    """
    # Retrieve the visibility mask for the agent
    agent_visibility_mask = observation["visibility_masks"][
        agent_id
    ]  # shape: (width, height)

    # Ensure the mask is boolean
    agent_visibility_mask = agent_visibility_mask.astype(bool)

    # Retrieve the full map
    full_map = observation["map"]  # shape: (width, height, features_per_tile)

    # Expand the mask to match the map's shape for broadcasting
    mask_expanded = agent_visibility_mask[:, :, np.newaxis]  # shape: (width, height, 1)

    # Apply the mask: set unseen tiles to mask_value
    # This will broadcast the mask across the features_per_tile dimension
    masked_map = np.where(mask_expanded, full_map, mask_value)

    y_coords, x_coords = np.where(agent_visibility_mask)
    return list(zip(x_coords, y_coords))

    # return masked_map
