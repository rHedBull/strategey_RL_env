from uuid import uuid1

from typing import Tuple


class City:

    def __init__(self, agent_id: int, position: Tuple[int, int]):

        self.id = uuid1()

        self.x, self.y  = position

        self.level = 0
        self.owner = agent_id # can change in theory

