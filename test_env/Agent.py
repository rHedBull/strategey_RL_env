import numpy as np


class Agent:

    def __init__(self, id):
        self.id = id
        self.env = None
        self.action = None
        self.q_table = None

    def get_action(self, possible_actions):
        action = np.random.choice(possible_actions)
        self.action = action
        return self.action

    def step(self):
        self.env.step(self.action)


