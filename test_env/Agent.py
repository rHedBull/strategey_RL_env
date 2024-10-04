import numpy as np


class Agent:
    def __init__(self, id):
        self.id = id
        self.state = None
        self.action = "Running"
        self.q_table = None

    def get_action(self, env_info, possible_actions):
        # action = np.random.choice(possible_actions)

        # action dictionary mask
        selected_action = {
            "move": {"direction": None, "new_position": None},
            "claim": None,  # position goes here
        }
        # expand default action dictionary mask
        self.action = 2

        x_max = 9  # env_info[0].shape[0]
        y_max = 9  # env_info[0].shape[1] # TODO change this to map bounds

        x = np.random.randint(0, x_max)
        y = np.random.randint(0, y_max)

        pos = [x, y]
        selected_action["claim"] = pos

        # TODO: vectorize and normalize the env_info here!!
        # TODO connect to Q-table or other RL algorithm
        return selected_action
