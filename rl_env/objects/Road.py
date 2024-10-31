from typing import Tuple

from rl_env.objects.MapObject import MapObject

road_types = {
    "horizontal"
    "vertical"
}

class Road(MapObject):

    def __init__(self, position: Tuple[int, int], road_type):
        super().__init__(position)
        self.max_level = 3

        if road_type not in road_types:
            raise ValueError(f"Invalid road type: {road_type}")
        self.road_type = road_type
