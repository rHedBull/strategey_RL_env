
from Map.Sim_Map import Map
from agents.Sim_Agent import Agent
from RL_env.Settings import Settings


class MapEnvironment:
    def __init__(self, settings_file, num_agents, render_game=False, screen=None):

        self.settings = Settings(settings_file)
        self.screen = screen
        self.render_mode = render_game
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
        # Apply the actions to the environment
        # Update the environment state
        # Calculate the reward
        # Check if the episode has ended
        # You'll need to define these
        rewards = []
        dones = []
        for action, agent in zip(actions, self.agents):
            self.apply_action(action, agent)
            reward = self.calculate_reward(agent)
            done = self.check_done(agent)
            rewards.append(reward)
            dones.append(done)
        return self.get_state(), rewards, dones, {}

    def render(self):

        if not self.render_mode:
            return

        self.map.draw(self.screen, 0, 0, 0)
        for agent in self.agents:
            agent.draw(self.screen, self.map.tile_size
                       , 0, 0, 0)

    def apply_action(self, action, agent):

        # this should be moved to the agent class if more complex
        if action == 'Claim':
            self.map.claim_tile(agent.x, agent.y, agent.id)
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

    def calculate_reward(self, agent):
        # Calculate the reward for the agent
        return 0

    def check_done(self, agent):
        if agent.state == 'Done':
            return True
        else:
            return False

    def get_state(self):
        states = []
        for agent in self.agents:
            state = agent.get_state()
            states.append(state)
        return states
