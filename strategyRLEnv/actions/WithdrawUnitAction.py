from strategyRLEnv.actions.Action import Action, ActionType
from strategyRLEnv.Agent import Agent
from strategyRLEnv.map.MapPosition import MapPosition


class WithdrawUnitAction(Action):
    def __init__(self, agent: Agent, position: MapPosition):
        super().__init__(agent, position, ActionType.UNIT)

    def validate(self, env) -> bool:
        if not super().validate(env):
            return False

        # check if visible for agent
        if not env.map.is_visible(self.position, self.agent.id):
            return False

        # check if there is a unit on the tile
        if env.map.get_tile(self.position).unit is None:
            return False

        # check if the unit is owned by the agent
        if env.map.get_tile(self.position).unit.owner.id != self.agent.id:
            return False

        return True

    def execute(self, env):
        unit = env.map.get_tile(self.position).unit
        env.map.get_tile(self.position).unit = None

        self.agent.remove_unit(unit)

        ratio = self.get_cost(env)  # in this case a ration how much is returned
        self.agent.money += unit.strength * ratio
        reward = unit.strength * ratio
        return reward

    def get_cost(self, env) -> float:
        """Return the cost of the action."""
        return env.env_settings.get("actions")["withdraw_unit"]["cost"]
