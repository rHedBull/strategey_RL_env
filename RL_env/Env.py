import pygame
import numpy as np

from Map.Sim_Map import Map
from RL_env.actions import ActionManager
from agents.Sim_Agent import Agent


def check_done(agent):
    if agent.state == 'Done':
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


class MapEnvironment:
    def __init__(self, env_settings, render_mode=False, screen=None,
                 game_mode='automated'):

        self.game_mode = game_mode
        self.settings = env_settings
        self.render_mode = render_mode
        self.screen = screen
        self.map = Map()
        self.map.create_map(self.settings)
        self.numb_agents = env_settings.get_setting('num_agents')
        self.agents = [Agent(i, self.game_mode) for i in range(self.numb_agents)]

        for agent in self.agents:
            agent.create_agent(self.settings, self.map.max_x_index, self.map.max_y_index)

        self.action_manager = ActionManager(self, env_settings)
        self.reset()

    def reset(self):

        self.map.reset()
        for agent in self.agents:
            agent.reset(self.settings)

    def step(self, actions, action_properties=None):

        rewards = []
        dones = []

        # make action order random
        # list of agent indices from 0 to number of agents
        agent_indices = [i for i in range(self.numb_agents)]
        np.random.shuffle(agent_indices)

        for agent_index in agent_indices:
            action = actions[agent_index]
            agent = self.agents[agent_index]
            action_property = action_properties[agent_index]

            self.action_manager.apply_action(action, agent, action_property)
            reward = calculate_reward(agent)
            done = check_done(agent)
            rewards.append(reward)
            dones.append(done)

        for agent in self.agents:
            agent.update()

        # TODO: update env state

        all_done = self.check_if_all_done(dones)
        return self.get_env_state(), rewards, dones, all_done

    def render(self):

        if not self.render_mode:
            return

        self.map.draw(self.screen, 0, 0, 0)
        for agent in self.agents:
            agent.draw(self.screen, self.map.tile_size, 0, 0, 0)
        pygame.display.flip()

    def get_env_state(self):

        map_info = self.map.get_observation_of_map_state()  # TODO include building info ?

        agent_info = np.zeros((len(self.agents), 3))
        for agent in self.agents:
            info = agent.get_state_for_env_info()
            agent_info[agent.id] = info

        env_info = [map_info, agent_info]
        return env_info

    def get_possible_actions(self, agent_id):

        possible_actions = []
        agent = self.agents[agent_id]
        possible_actions.append(agent.get_possible_actions())

        return possible_actions

    def check_if_all_done(self, dones):
        # check if all in dones are true

        for i in dones:
            if not i:
                return False

        self.finish_env()
        return True

    def finish_env(self):
        print("Game Terminated")
        if self.render_mode:
            print("Press any key to close the window")
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
