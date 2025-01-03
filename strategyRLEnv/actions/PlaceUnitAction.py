from typing import Tuple

from strategyRLEnv.actions.Action import Action, ActionType
from strategyRLEnv.Agent import Agent
from strategyRLEnv.map.map_settings import OWNER_DEFAULT_TILE
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

        return True

    def execute(self, env):
        unit = Unit(self.agent, self.position)

        tile = env.map.get_tile(self.position)
        if tile.owner_id != OWNER_DEFAULT_TILE and tile.owner_id != self.agent.id:
            # also claim the tile
            env.map.claim_tile(self.agent, self.position)
            self.agent.add_claimed_tile(self.position)
            self.agent.update_local_visibility(self.position)

        self.agent.units.append(unit)

        self.agent.money -= self.get_cost(env)
        reward = 0
        return reward

    def get_cost(self, env) -> float:
        """Return the cost of the action."""
        return env.env_settings.get("actions")["place_unit"]["cost"]
