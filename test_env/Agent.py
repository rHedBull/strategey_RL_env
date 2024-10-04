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
            "move": None,
            "claim": {"x": None, "y": None},
        }
        # expand default action dictionary mask
        self.action = 2

        x_max = 9  # env_info[0].shape[0]
        y_max = 9  # env_info[0].shape[1] # TODO change this to map bounds

        selected_action["claim"]["x"] = np.random.randint(0, x_max)
        selected_action["claim"]["y"] = np.random.randint(0, y_max)

        # TODO: vectorize and normalize the env_info here!!
        # TODO connect to Q-table or other RL algorithm
        return selected_action
