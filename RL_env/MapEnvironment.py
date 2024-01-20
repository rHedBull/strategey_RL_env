import pygame
import numpy as np

from Map.Sim_Map import Map
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
    def __init__(self, settings_file, num_agents, render_mode=False, screen=None, game_mode='automated'):

        self.game_mode = game_mode
        self.settings = settings_file
        self.render_mode = render_mode
        self.screen = screen
        self.map = Map()
        self.map.create_map(self.settings)
        self.agents = [Agent(i, self.game_mode) for i in range(num_agents)]
        for agent in self.agents:
            agent.create_agent(self.settings, self.map.max_x_index, self.map.max_y_index)

        self.reset()

    def reset(self):

        self.map.reset()
        for agent in self.agents:
            agent.reset()

    def step(self, actions):

        rewards = []
        dones = []
        for action, agent in zip(actions, self.agents):
            self.apply_action(action, agent)
            reward = calculate_reward(agent)
            done = check_done(agent)
            rewards.append(reward)
            dones.append(done)

        # TODO update environment state
        for agent in self.agents:
            agent.update()

        all_done = self.check_if_all_done(dones)
        return self.get_env_state(), rewards, dones, all_done

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

    def render(self):

        if not self.render_mode:
            return

        self.map.draw(self.screen, 0, 0, 0)
        for agent in self.agents:
            agent.draw(self.screen, self.map.tile_size, 0, 0, 0)
        pygame.display.flip()

    def apply_action(self, action, agent):

        if action == 'None' or agent.state == 'Done':
            return

        # this should be moved to the agent class if more complex
        if action == 4:
            self.map.claim_tile(agent)
            agent.claimed_tiles.append(self.map.get_tile(agent.x, agent.y))
            return

        if action == 2:
            agent.x -= 1
        elif action == 3:
            agent.x += 1
        elif action == 0:
            agent.y -= 1
        elif action == 1:
            agent.y += 1

        agent.x = max(0, min(agent.x, self.map.max_x_index - 1))
        agent.y = max(0, min(agent.y, self.map.max_y_index - 1))

    def get_env_state(self):

        map_info = self.map.get_map_as_matrix()

        agent_info = np.zeros((len(self.agents), 3))
        for agent in self.agents:
            info = agent.get_state_for_env_info()
            agent_info[agent.id] = info

        env_info = [map_info, agent_info]
        return env_info

    def get_possible_actions(self):
        return [0, 1, 2, 3, 4]
