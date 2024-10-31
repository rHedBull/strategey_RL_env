import random as rd


class Agent:
    def __init__(self, id, x_max, y_max):
        self.id = id
        self.state = None
        self.action = "Running"
        self.q_table = None
        self.x_max = x_max
        self.y_max = y_max

        self.reward = 0

    def get_action(self, env_info, possible_actions):
        # action dictionary mask
        selected_action = []

        # expand default action dictionary mask
        self.action = 2

        claimable_tiles = possible_actions[0]

        # select a random tile from set
        pos = rd.choice(list(claimable_tiles))

        claim_action = {
                "type":"claim",
                "props": {"position": pos}
        }

        selected_action.append(claim_action)
        # TODO add more advanced action selection here

        city_action = {
                "type":"city",
                "props": {"position": pos}
        }
        #cselected_action.append(city_action)

        move_action = {
            "type": "move",
            "props": {"direction": 4}
        }
        selected_action.append(move_action)

        # TODO: vectorize and normalize the env_info here!!
        # TODO connect to Q-table or other RL algorithm
        return selected_action

    def update(self, reward):
        self.reward += reward
