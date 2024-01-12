import uuid

import pygame

from RL_env.Settings import Settings
from test_env.Agent import Agent
from test_env.Player import Player


class Run:
    def __init__(self, settings_file, hyperparameters_file, env):
        self.id = uuid.uuid4()
        self.settings = Settings(settings_file)
        self.hyper_settings = Settings(hyperparameters_file)
        self.max_steps = self.settings.get_setting('max_steps')
        self.num_agents = self.settings.get_setting('num_agents')
        self.agents = []
        self.env = env

    def check_settings(self):
        pass

    # TODO chekc if settings are valid
    # TODO check if hyperparameters are valid
    # TODO check if map creation parameters fit
    # TODO check if number agents is correct as env agents

    def run(self):
        pygame.init()

        # setup my agents
        self.agents = [Player()]
        for i in range(self.num_agents - 1):
            agent = Agent(i)
            self.agents.append(agent)

        # run the game loop
        done = False
        step = 0
        # list of agents that are still running, by index in agents list
        running_agents = [i for i in range(self.num_agents)]
        while not done and step < self.max_steps:
            self.env.render()  # checks already if rendering is on

            # get actions from agents
            agent_actions = []
            for agent in self.agents:
                if agent.state == 'Done':
                    agent_actions.append('None')
                    continue
                # if agent is a player, get action from keyboard
                if isinstance(agent, Player):
                    action = agent.get_action(pygame)
                    print("Player chose action {}".format(action))
                else:
                    possible_actions = ['Move Up', 'Move Down', 'Move Left', 'Move Right']
                    action = agent.get_action(possible_actions)
                agent_actions.append(action)

            state, reward, dones, all_done = self.env.step(agent_actions)

            for i, done in zip(running_agents, dones):
                if done:
                    print("Agent {} is done".format(i))
                    self.agents[i].state = 'Done'

            running_agents = [agent for agent, done in zip(running_agents, dones) if not done]

            # check if the game is over
            if all_done:
                print("game done")

