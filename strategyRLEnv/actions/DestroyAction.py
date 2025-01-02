from strategyRLEnv.actions.Action import Action, ActionType
from strategyRLEnv.Agent import Agent
from strategyRLEnv.map.map_settings import OWNER_DEFAULT_TILE
from strategyRLEnv.map.MapPosition import MapPosition


class DestroyAction(Action):
    def __init__(self, agent: Agent, position: MapPosition):
        super().__init__(agent, position, ActionType.CLAIM)

    def validate(self, env) -> bool:
        if not super().validate(env):
            return False

        tile = env.map.get_tile(self.position)

        if tile.get_building() is None:
            return False

        if tile.get_owner() != OWNER_DEFAULT_TILE and tile.get_owner() != self.agent.id:
            return False

        # check if visible for agent
        if not env.map.is_visible(self.position, self.agent.id):
            return False

        return True

    def execute(self, env) -> int:
        building = env.map.get_tile(self.position).get_building()
        income = building.get_income()
        env.map.get_tile(self.position).update(env)
        env.map.remove_building(self.position)  # remove no matter what

        self.agent.money -= env.action_manager.actions_definition["claim"]["cost"]
        recuperation_factor = env.action_manager.actions_definition["claim"]["reward"]
        money_return = income * recuperation_factor
        return money_return
