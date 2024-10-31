from abc import ABC
from uuid import uuid1

from typing import Tuple


class MapObject(ABC):

    def __init__(self, position: Tuple[int, int]):

        self.id = uuid1()

        self.x, self.y  = position

        self.level = 0
        self.max_level = None

    def upgrade(self):
        new_level = self.level + 1
        self.level = min(new_level, self.max_level)


    def downgrade(self):
        new_level = self.level -1
        self.level = max(new_level, 0)

