from Map.MapSettings import OWNER_DEFAULT_TILE

buildings = [[],['improvement-1', 100, 5]]

# TODO : implement graphical building visualization


class ActionManager:
    def __init__(self, env, env_settings):
        self.env = env
        self.env_settings = env_settings
        self.actions_definition = self.env_settings.get_setting('actions')

    def apply_action(self, action_index, agent, action_properties):

        if action_index <= 0 or agent.state == 'Done':
            return

        action_name = self.actions_definition[action_index]['name']

        if action_name == 'move':
            self.move_agent(agent, action_index, action_properties)
        elif action_name == 'claim':
            self.claim_tile(agent, action_index, action_properties)
        elif action_name == 'build':
            self.add_building(agent, action_index, action_properties)
        else:
            return

    def claim_tile(self, agent, action_index, action_properties):
        base_claim_cost = self.actions_definition[action_index]['cost']
        x = action_properties[0]
        y = action_properties[1]

        if not self.check_claim_cost(agent, base_claim_cost, x, y):
            return

        self.env.map.claim_tile(agent, x, y)
        agent.claimed_tiles.append(self.env.map.get_tile(x, y))

    def check_claim_cost(self, agent, base_claim_cost, x, y):

        # check if properties correctly defined
        if x < 0 or y < 0 or x > self.env.map.max_x_index or y > self.env.map.max_y_index or None in [x, y]:
            return False

        # check if the tile is already claimed by someone
        if self.env.map.squares[x][y].get_owner() != OWNER_DEFAULT_TILE:
            return False
        # TODO add some conflict hanlding here or just increased tile purchase cost

        # check if enough money to claim tile
        if agent.money < base_claim_cost:
            return True
        # all checks passed
        return True

    def add_building(self, agent, action_index, action_properties):
        x = action_properties[0]
        y = action_properties[1]
        base_construction_cost = self.actions_definition[action_index]['cost']

        building_id = action_properties[2]

        if not self.check_building_cost(agent, base_construction_cost, building_id, x, y):
            return

        #self.env.map.add_building(building_id, x, y)

    def check_building_cost(self, agent, base_construction_cost, building_id, x, y):
        specific_building_cost = buildings[building_id][1]

        total_cost = base_construction_cost + specific_building_cost
        if agent.money < total_cost:
            return False

        # check if building is possible
        tile_for_planned_building = self.env.map.get_tile(x, y)

        # check if agent owns the tile to build on
        if tile_for_planned_building.get_owner() != agent:
            return False

        current_buildings_on_tile = tile_for_planned_building.get_buildings()

        # check if building already exists
        for building in current_buildings_on_tile:
            if building == building_id:
                return False

        # all checks passed
        return True

    def move_agent(self, agent, action_index, action_properties):

        direction = action_properties[0]

        move_cost = self.actions_definition[action_index]['cost']

        if not self.check_move_cost(agent, move_cost):
            return

        if direction == 0:  # left
            agent.x -= 1

        elif direction == 1:  # right
            agent.x += 1

        elif direction == 2:  # up
            agent.y -= 1
        elif direction == 3:  # down
            agent.y += 1

        agent.money -= move_cost
        agent.x = max(0, min(agent.x, self.env.map.max_x_index - 1))
        agent.y = max(0, min(agent.y, self.env.map.max_y_index - 1))

    def check_move_cost(self, agent, basic_move_cost):

        if agent.money < basic_move_cost:
            return False

        # all checks passed
        return True
