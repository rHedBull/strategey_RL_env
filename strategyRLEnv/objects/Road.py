from typing import Dict, Tuple

import pygame

from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.objects.Building import Building
from strategyRLEnv.map.map_settings import BuildingType

road_color = (128, 128, 128)

# brown bridge
bridge_color = (139, 69, 19)


class RoadShape:
    up: bool = False
    down: bool = False
    left: bool = False
    right: bool = False


class Road(Building):
    def __init__(self, position: MapPosition, building_parameters: Dict, shape=None):
        super().__init__(position, BuildingType.ROAD, building_parameters)

        self.shape = shape if shape else RoadShape()
        self.shape.left = True

    def draw(
        self,
        screen: pygame.Surface,
        square_size: int,
        owner_color: Tuple[int, int, int],
    ):
        """
        Draw the road on the screen.
        :param owner_color:
        :param square_size:
        :param screen: Pygame display surface
        """

        draw_bridge_road(
            screen,
            self.position.x,
            self.position.y,
            square_size,
            self.shape,
            road_color,
        )


class Bridge(Building):
    def __init__(self, position: MapPosition, building_parameters: Dict, shape=None):
        super().__init__(position, BuildingType.BRIDGE, building_parameters)

        self.max_level = 3
        self.shape = shape if shape else RoadShape()

    def draw(
        self,
        screen: pygame.Surface,
        square_size: int,
        owner_color: Tuple[int, int, int],
    ):
        """
        Draw the road on the screen.
        :param shape:
        :param square_size:
        :param owner_color:
        :param screen: Pygame display surface
        """

        draw_bridge_road(
            screen,
            self.position.x,
            self.position.y,
            square_size,
            self.shape,
            bridge_color,
        )


def update_road_bridge_shape(road_or_bridge, map):
    """
    Update the road shape of the tile at the given position based on surrounding roads and bridges.

    :param map: Map object
    :param position: MapPosition
    """
    x = road_or_bridge.position.x
    y = road_or_bridge.position.y

    # Check surrounding tiles for roads and bridges

    up = map.get_tile(MapPosition(x, y - 1))
    down = map.get_tile(MapPosition(x, y + 1))
    left = map.get_tile(MapPosition(x - 1, y))
    right = map.get_tile(MapPosition(x + 1, y))

    # Update road shape based on surrounding roads and bridges
    shape = RoadShape()
    if up:
        shape.up = up.has_any_building()
    else:
        shape.up = False

    if down:
        shape.down = down.has_any_building()
    else:
        shape.down = False

    if left:
        shape.left = left.has_any_building()
    else:
        shape.left = False

    if right:
        shape.right = right.has_any_building()
    else:
        shape.right = False

    # if all directions are false, set left to true
    if not any([shape.up, shape.down, shape.left, shape.right]):
        shape.left = True

    else:
        # update surrounding tiles
        if shape.up:
            if up.has_road() or up.has_bridge():
                up.get_road_or_bridge().shape.down = True
        if shape.down:
            if down.has_road() or down.has_bridge():
                down.get_road_or_bridge().shape.up = True
        if shape.left:
            if left.has_road() or left.has_bridge():
                left.get_road_or_bridge().shape.right = True
        if shape.right:
            if right.has_road() or right.has_bridge():
                right.get_road_or_bridge().shape.left = True

    road_or_bridge.shape = shape


def draw_bridge_road(
    screen: pygame.Surface,
    x,
    y,
    square_size: int,
    shape: RoadShape,
    color: Tuple[int, int, int],
):
    """
    Draw the road on the screen based on the RoadShape.

    :param color:
    :param y:
    :param x:
    :param screen: Pygame display surface
    :param square_size: Size of the square tile
    :param shape: RoadShape indicating connections
    """
    center_x = x * square_size + square_size // 2
    center_y = y * square_size + square_size // 2
    half_size = square_size // 2

    road_width = max(2, square_size // 8)  # Adjust road thickness as needed

    # Define end points for each direction
    directions = {
        "up": (center_x, center_y - half_size),
        "down": (center_x, center_y + half_size),
        "left": (center_x - half_size, center_y),
        "right": (center_x + half_size, center_y),
    }

    # Draw roads based on active connections
    if shape.up:
        pygame.draw.line(
            screen, color, (center_x, center_y), directions["up"], road_width
        )
    if shape.down:
        pygame.draw.line(
            screen, color, (center_x, center_y), directions["down"], road_width
        )
    if shape.left:
        pygame.draw.line(
            screen, color, (center_x, center_y), directions["left"], road_width
        )
    if shape.right:
        pygame.draw.line(
            screen, color, (center_x, center_y), directions["right"], road_width
        )
