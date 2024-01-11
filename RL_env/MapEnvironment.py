import pygame

from Map.Sim_Map import Map
from agents.Sim_Agent import Agent
from RL_env.Settings import Settings


def check_done(agent):
    if agent.state == 'Done':
        return True
    else:
        return False


def calculate_reward(agent):
    if check_done(agent):
        return agent.budget + 1000
    else:
        return agent.budget


class MapEnvironment:
    def __init__(self, settings_file, num_agents, render_mode=False, screen=None):

        self.settings = Settings(settings_file)
        self.render_mode = render_mode
        self.screen = screen
        self.map = Map()
        self.map.create_map(self.settings)
        self.agents = [Agent(i) for i in range(num_agents)]
        for agent in self.agents:
            agent.create_agent(self.settings, self.map.max_x_index, self.map.max_y_index)

        self.reset()

    def reset(self):

        self.map.reset()
        for agent in self.agents:
            agent.reset()
        return self.get_state()

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

        all_done = self.check_if_all_done(dones)
        return self.get_state(), rewards, dones, all_done

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
                    if event.type == pygame.QUIT:
                        running = False
            pygame.quit()
        else:
            pygame.quit()

    def render(self):

        if not self.render_mode:
            return

        self.map.draw(self.screen, 0, 0, 0)
        for agent in self.agents:
            agent.draw(self.screen, self.map.tile_size
                       , 0, 0, 0)
        pygame.display.flip()

    def apply_action(self, action, agent):

        if action == 'None' or agent.state == 'Done':
            return

        # this should be moved to the agent class if more complex
        if action == 'Claim':
            self.map.claim_tile(agent)
            return

        if action == 'Move Left':
            agent.x -= 1
        elif action == 'Move Right':
            agent.x += 1
        elif action == 'Move Up':
            agent.y -= 1
        elif action == 'Move Down':
            agent.y += 1

        agent.x = max(0, min(agent.x, self.map.max_x_index - 1))
        agent.y = max(0, min(agent.y, self.map.max_y_index - 1))

        agent.budget = agent.budget - 1
        agent.update()

    def get_state(self):
        states = []
        for agent in self.agents:
            state = agent.get_state()
            states.append(state)
        return states
