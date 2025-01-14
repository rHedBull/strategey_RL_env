from strategyRLEnv.actions.Action import Action, ActionType
from strategyRLEnv.actions.BuildAction import (fit_building_to_land_type)
from strategyRLEnv.Agent import Agent
from strategyRLEnv.map.map_settings import (OWNER_DEFAULT_TILE,
                                            conquer_threshold, discovery_reward)
from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.objects.Unit import Unit


class PlaceUnitAction(Action):
    def __init__(self, agent: Agent, position: MapPosition):
        super().__init__(agent, position, ActionType.UNIT)

    def validate(self, env) -> bool:
        if not super().validate(env):
            return False

        # check if visible for agent
        if not env.map.is_visible(self.position, self.agent.id):
            return False

        if not fit_building_to_land_type(env, self.position, "UNIT"):
            return False

        if not check_if_claiming_enemy_tile(env, self.position, self.agent.id):
            return False

        # check if there is a enemy unit on the tile
        tile = env.map.get_tile(self.position)
        if tile.unit is not None:
            if tile.unit.owner.id != self.agent.id:
                return False

        return True

    def execute(self, env):
        tile = env.map.get_tile(self.position)
        discovery = 0
        if tile.owner_id != OWNER_DEFAULT_TILE and tile.owner_id != self.agent.id:
            # also claim the tile
            env.map.claim_tile(self.agent, self.position)
            self.agent.add_claimed_tile(self.position)
            discovery = self.agent.update_local_visibility(self.position)

        if tile.unit is not None and tile.unit.owner.id == self.agent.id:
            # add strength to unit
            tile.unit.increase_strength(env, 50)

        else:
            unit = Unit(self.agent, self.position)
            env.agents[self.agent.id].add_unit(unit)
            env.map.add_unit(unit, self.position)
            discovery = self.agent.update_local_visibility(self.position)

        self.agent.money -= self.get_cost(env)
        reward = discovery * discovery_reward
        return reward

    def get_cost(self, env) -> float:
        """Return the cost of the action."""
        return env.env_settings.get("actions")["place_unit"]["cost"]


def check_if_claiming_enemy_tile(env, position: MapPosition, agent_id: int) -> bool:
    tile = env.map.get_tile(position)
    if tile.owner_id != OWNER_DEFAULT_TILE and tile.owner_id != agent_id:
        surrounding = env.map.get_surrounding_tiles(position, 1, diagonal=True)
        friendly_unit_count = 0
        for tile in surrounding:
            if tile.unit is not None and tile.unit.owner.id == agent_id:
                friendly_unit_count += 1
        if friendly_unit_count >= conquer_threshold:
            return True
        else:
            return False
    # our own tile
    return True
