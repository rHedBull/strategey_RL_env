from typing import Tuple

from rl_env.objects.MapObject import MapObject


class City(MapObject):

    def __init__(self, agent_id: int, position: Tuple[int, int]):
        super().__init__(position)

        self.owner = agent_id # can change in theory
        self.max_level = 3
