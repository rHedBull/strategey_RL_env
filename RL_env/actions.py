from Map.MapSettings import OWNER_DEFAULT_TILE

action_dictionary = {
    'Move Up': 0,
    'Move Down': 1,
    'Move Left': 2,
    'Move Right': 3,
    'Claim': 4,
    'build': 5
}

buildings = [['improvement-1', 100, 5]]


# TODO : one system to manage actions and buildings, preferable over: [ []]
# TODO : implement graphical building visualization

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

        if action == -1 or agent.state == 'Done':
            return

        if not self.check_cost(agent, action, action_properties):
            return

        if action == 4:
            self.claim_tile(agent, action_properties[0], action_properties[1])
            return

        if action == 5:  # build something
            x = action_properties[0]
            y = action_properties[1]
            building_id = action_properties[2]

        # TODO remove option to move
        self.move_agent(agent, action)

    def check_cost(self, agent, action, action_properties):
        # if action is move up, down, left, right

        if action < 4:
            x = agent.x
            y = agent.y

            if agent.money >= self.action_cost.get_setting('move_one'):

                # check for map bounds
                if x < 0 or x > self.env.map.max_x_index - 1 or y < 0 or y > self.env.map.max_y_index - 1:
                    return False
                else:
                    return True

        elif action == 4:

            claim_cost = self.action_cost.get_setting('claim_one_tile')

            #check if the tile is already claimed by someone
            x = action_properties[0]
            y = action_properties[1]
            tile_claim_id = tile_build = y * self.env.map.max_x_index + x

            if self.env.map.squares[x][y].get_owner() != OWNER_DEFAULT_TILE:
                return False
                # TODO add some conflict hanlding here or just increased tile purchase cost


            # check if enough money to claim tile
            if agent.money >= claim_cost:
                return True

        elif action == 5:
            # check if building is possible
            x = action_properties[0]
            y = action_properties[1]
            building_id = action_properties[2]
            building_cost = buildings[building_id]
            current_buildings_on_tile = self.env.map.get_tile(x, y).buildings

            # check if building is possible

            # check if agent owns the tile to build on
            claimed_tiles = agent.claimed_tiles
            tile_build = y * self.env.map.max_x_index + x

            tile_owned = False
            for tile in claimed_tiles:
                if tile == tile_build:
                    tile_owned = True
                    continue

            if not tile_owned:
                return False

            # check if building already exists
            for building in current_buildings_on_tile:
                if building[0] == building_id:
                    return False
            if building_cost <= agent.money:
                return True
            else:
                return False

        return False

    def claim_tile(self, agent, x, y):

        self.env.map.claim_tile(agent, x, y)
        agent.claimed_tiles.append(self.env.map.get_tile(x, y))

    def add_building(self, building_id, x, y):
        self.env.map.add_building(building_id, x, y)

    def move_agent(self, agent, action):

        if action == 2:
            agent.x -= 1

        elif action == 3:
            agent.x += 1

        elif action == 0:
            agent.y -= 1
        elif action == 1:
            agent.y += 1

            agent.money -= self.action_cost.get_setting('move_one')

        agent.x = max(0, min(agent.x, self.env.map.max_x_index - 1))
        agent.y = max(0, min(agent.y, self.env.map.max_y_index - 1))