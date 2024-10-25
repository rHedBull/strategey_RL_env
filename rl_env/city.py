from uuid import uuid1

from typing import Tuple

max_level = 3
class City:

    def __init__(self, agent_id: int, position: Tuple[int, int]):

        self.id = uuid1()

        self.x, self.y  = position

        self.level = 0
        self.owner = agent_id # can change in theory

    def upgrade(self):
        new_level = self.level + 1
        self.level = min(new_level, max_level)


    def downgrade(self):
        new_level = self.level -1
        self.level = max(new_level, 0)

