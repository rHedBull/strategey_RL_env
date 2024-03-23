import uuid
from datetime import datetime

import tensorflow as tf
import pygame

from RL_env.MapEnvironment import capture_game_state_as_image
from test_env.Agent import Agent
from test_env.Player import Player


class Run:
    def __init__(self, settings_file, hyperparameters, env):
        self.id = uuid.uuid4()
        self.settings = settings_file

        self.hyper_settings = hyperparameters
        self.max_steps = self.settings.get_setting('max_steps')
        self.num_agents = self.settings.get_setting('num_agents')
        self.agents = []
        self.env = env

        current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_dir = 'test_env/logs/agent_performance/' + current_time
        self.summary_writer = tf.summary.create_file_writer(log_dir)

    def run(self):
        pygame.init()

        self.setup_agents()

        # run the game loop
        step = 0
        # list of agents that are still running, by index in agents list
        running_agents = [i for i in range(self.num_agents)]
        all_done = False

        common_env_state = self.env.get_env_state()  # TODO different types of observability for different agents
        while not all_done and step < self.max_steps:
            self.env.render()  # checks already if rendering is on

            # get actions from agents
            agent_actions = []
            action_properties = []
            agent_rewards = []

            for agent in self.agents:
                if agent.state == 'Done':
                    agent_actions.append(-1)
                    continue
                # if agent is a player, get action from keyboard
                if isinstance(agent, Player):
                    action, action_properties = agent.get_action(pygame)
                    print("Player chose action {}".format(action))
                else:
                    possible_actions = self.env.get_possible_actions(agent.id)
                    action, action_properties = agent.get_action(common_env_state, possible_actions)
                agent_actions.append(action)

            common_env_state, agent_rewards, dones, all_done = self.env.step(agent_actions, action_properties)

            self.update_agents(all_done, running_agents, dones)
            self.log_stats(agent_rewards, step, agent_actions)
            step += 1

    def log_stats(self, reward, step, actions):
        if step % self.settings.get_setting('storing_round_interval') == 0:

            with self.summary_writer.as_default():
                for i, agent in enumerate(self.agents):
                    tf.summary.scalar('reward_agent_{}'.format(i), reward[i], step)
                    tf.summary.scalar('action_agent_{}'.format(i), actions[i], step)

        if step % self.settings.get_setting('image_logging_round_interval') == 0:
            game_state_image = capture_game_state_as_image()
            tensor_img = tf.convert_to_tensor(game_state_image, dtype=tf.uint8)
            tensor_img = tf.expand_dims(tensor_img, 0)  # Add the batch dimension
            with self.summary_writer.as_default():
                tf.summary.image("Step: " + str(step), tensor_img, step)

    def update_agents(self, all_done, running_agents, dones):
        for i, done in zip(running_agents, dones):
            if done:
                if isinstance(self.agents[i], Player):
                    print("Player {} is done".format(i))
                else:
                    print("Agent {} is done".format(i))
                self.agents[i].state = 'Done'

        running_agents = [agent for agent, done in zip(running_agents, dones) if not done]

        # check if the game is over
        if all_done:
            print("game done")

    def setup_agents(self):
        if self.settings.get_setting('playable_game'):
            self.agents = [Player()]
            for i in range(self.num_agents - 1):
                agent = Agent(i)
                self.agents.append(agent)
        else:
            for i in range(self.num_agents):
                agent = Agent(i)
                self.agents.append(agent)
