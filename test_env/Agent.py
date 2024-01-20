import numpy as np


class Agent:

    def __init__(self, id):
        self.id = id
        self.state = None
        self.action = 'Running'
        self.q_table = None

    def get_action(self, env_info, possible_actions):
        action = np.random.choice(possible_actions)
        self.action = action
        return self.action
