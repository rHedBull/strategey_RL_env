action_dictionary = {
    'Move Up': 0,
    'Move Down': 1,
    'Move Left': 2,
    'Move Right': 3,
    'Claim': 4
}


class ActionManager:
    def __init__(self, env, cost):
        self.env = env
        self.action_to_int = action_dictionary
        self.int_to_action = {v: k for k, v in self.action_to_int.items()}
        self.action_cost = cost

    def get_action_name(self, action_int):
        return self.int_to_action.get(action_int, "Unknown")

    def get_action_int(self, action_name):
        return self.action_to_int.get(action_name, -1)

    def apply_action(self, action, agent, action_properties):

        if action == 'None' or agent.state == 'Done':
            return

        if not self.check_cost(agent, action):
            return

        if action == 4:
            self.claim_tile(agent, action_properties[0], action_properties[1])
            return


        # TODO remove option to move
        if action == 2:
            agent.x -= 1
        elif action == 3:
            agent.x += 1
        elif action == 0:
            agent.y -= 1
        elif action == 1:
            agent.y += 1

        agent.x = max(0, min(agent.x, self.env.map.max_x_index - 1))
        agent.y = max(0, min(agent.y, self.env.map.max_y_index - 1))

    def check_cost(self, agent, action):
        # if action is move up, down, left, right
        if action < 4:
            if agent.money >= self.action_cost.get_setting('move_one'):
                return True

        elif action == 4:
            if agent.money >= self.action_cost.get_setting('claim_one_tile'):
                return True

        return False

    def claim_tile(self, agent, x, y):
        # TODO implement action check map bounds
        # TODO implement claimng of tiles not standing on

        self.env.map.claim_tile(agent, x, y)
        agent.claimed_tiles.append(self.env.map.get_tile(x, y))
