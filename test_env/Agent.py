import numpy as np


class Agent:

    def __init__(self, id):
        self.id = id
        self.state = None
        self.action = 'Running'
        self.q_table = None

    def get_action(self, env_info, possible_actions):
        #action = np.random.choice(possible_actions)
        self.action = 4
        action_properties = [np.random.randint(0, 10), np.random.randint(0, 10)] # TODO change this to map bounds
        # TODO connect to Q-table or other RL algorithm
        return self.action, action_properties
