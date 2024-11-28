from unittest.mock import Mock

import pytest

from map.map_settings import (COLOR_DEFAULT_BORDER, OWNER_DEFAULT_TILE,
                              LandType, land_type_color)
from map.map_square import Map_Square
from map.MapPosition import MapPosition
from rl_env.objects.Building import BuildingType
from rl_env.objects.city import City
from rl_env.objects.Farm import Farm
from rl_env.objects.Road import Bridge, Road


@pytest.fixture
def map_square():
    """
    Fixture to create a Map_Square instance before each test.
    """
    return Map_Square(1, MapPosition(5, 10), land_value=LandType.LAND)


def test_initialization(map_square):
    """
    Test that Map_Square initializes correctly with given parameters.
    """
    assert map_square.tile_id == 1
    assert map_square.position.x == 5
    assert map_square.position.y == 10
    assert map_square.land_type == LandType.LAND
    assert map_square.height == 0
    assert map_square.precepitation == 0
    assert map_square.temperature == 0
    assert map_square.biome == 0
    assert map_square.resources == []
    assert map_square.owner_id == OWNER_DEFAULT_TILE
    assert map_square.visibility_bitmask == 0
    assert map_square.buildings == set()
    assert map_square.building_int == 0
    assert map_square.land_money_value == 1
    assert map_square.default_border_color == COLOR_DEFAULT_BORDER
    assert map_square.default_color == land_type_color(LandType.LAND)
    assert map_square.land_type_color == land_type_color(LandType.LAND)
    assert map_square.owner_color == COLOR_DEFAULT_BORDER


def test_reset(map_square):
    """
    Test that the reset method restores the initial state.
    """

    mock_agent_id = 7
    city = City(mock_agent_id, map_square.position, 1)

    # Modify some attributes
    map_square.owner_id = 2
    map_square.visibility_bitmask = 255
    map_square.land_type = LandType.MOUNTAIN
    map_square.land_type_color = land_type_color(LandType.MOUNTAIN)
    map_square.land_money_value = 5
    map_square.buildings.add(city)
    map_square.building_int = 1

    # Call reset
    map_square.reset()

    # Assertions
    assert map_square.owner_id == OWNER_DEFAULT_TILE
    assert map_square.visibility_bitmask == 0
    assert map_square.land_type == LandType.LAND
    assert map_square.land_type_color == land_type_color(LandType.LAND)
    assert map_square.owner_color == COLOR_DEFAULT_BORDER
    assert map_square.land_money_value == 1
    assert map_square.buildings == set()
    assert map_square.building_int == 0


def test_set_and_get_owner(map_square):
    """
    Test setting and getting the owner of the map square.
    """
    agent_id = 42
    agent_color = (128, 0, 128)  # Purple

    assert map_square.get_owner() == OWNER_DEFAULT_TILE

    # Set owner
    map_square.set_owner(agent_id, agent_color)

    # Assertions
    assert map_square.get_owner() == agent_id
    assert map_square.owner_color == agent_color


def test_set_and_get_land_type(map_square):
    """
    Test setting and getting the land type of the map square.
    """
    new_land_type = LandType.MOUNTAIN
    map_square.set_land_type(new_land_type)
    assert map_square.get_land_type() == new_land_type
    assert map_square.land_type_color == land_type_color(new_land_type)

    # Setting the same land type should not change anything
    map_square.set_land_type(new_land_type)
    assert map_square.get_land_type() == new_land_type
    assert map_square.land_type_color == land_type_color(new_land_type)


def test_claim(map_square):
    """
    Test claiming the map square by an agent.
    """
    agent = Mock()
    agent.id = 7
    agent.color = (0, 255, 0)  # Green

    assert map_square.owner_id == OWNER_DEFAULT_TILE
    assert map_square.owner_color == COLOR_DEFAULT_BORDER

    map_square.claim(agent)

    assert map_square.owner_id == agent.id
    assert map_square.owner_color == agent.color


def test_add_building(map_square):
    """
    Test adding a building to the map square.
    """

    mock_agent_id = 7
    city = City(mock_agent_id, map_square.position, 1)

    assert city not in map_square.buildings
    assert map_square.building_int == 0

    map_square.add_building(city)

    assert city in map_square.buildings
    assert map_square.building_int == 1


def test_has_building(map_square):
    """
    Test checking for specific building types.
    """

    mock_agent_id = 7
    city = City(mock_agent_id, map_square.position, 1)
    road = Road(map_square.position, 2)

    assert map_square.has_building(BuildingType.CITY) is False
    assert map_square.has_building(BuildingType.ROAD) is False

    map_square.add_building(city)
    assert map_square.has_building(BuildingType.CITY) is True
    assert map_square.has_building(BuildingType.ROAD) is False
    map_square.remove_building(city)

    map_square.add_building(road)
    assert map_square.has_building(BuildingType.ROAD) is True
    assert map_square.has_building(BuildingType.CITY) is False

    # Test undefined building type
    assert map_square.has_building("UNKNOWN_BUILDING") is False


def test_has_any_building(map_square):
    """
    Test checking if any building exists on the map square.
    """
    assert map_square.has_any_building() is False

    mock_agent_id = 7
    city = City(mock_agent_id, map_square.position, 1)

    map_square.add_building(city)
    assert map_square.has_any_building() is True


def test_remove_building(map_square):
    """
    Test removing a building from the map square.
    """

    mock_agent_id = 7
    city = City(mock_agent_id, map_square.position, 1)
    road = Road(map_square.position, 2)

    map_square.add_building(city)
    assert map_square.has_any_building() is True
    assert map_square.building_int == 1
    assert city in map_square.buildings

    # Remove city
    map_square.remove_building(city)
    assert map_square.has_any_building() is False
    assert map_square.building_int == 0
    assert city not in map_square.buildings

    # Add road
    map_square.add_building(road)
    assert map_square.has_any_building() is True
    assert map_square.building_int == 2
    assert road in map_square.buildings

    # Remove road
    map_square.remove_building(road)
    assert road not in map_square.buildings
    assert map_square.building_int == 0
    assert map_square.has_any_building() is False

    # Attempting to remove a non-existent building should do nothing
    map_square.remove_building(city)  # Already removed
    assert map_square.building_int == 0


def test_get_full_info(map_square):
    """
    Test retrieving the full info of the map square.
    """
    mock_building_id = 3
    mock_owner_agent = 7
    map_square.set_land_type(LandType.MOUNTAIN)
    map_square.set_owner(mock_owner_agent, (255, 0, 0))  # Red
    building = City(mock_owner_agent, MapPosition(0, 0), mock_building_id)
    map_square.add_building(building)

    expected_state = [
        LandType.MOUNTAIN.value,
        mock_owner_agent,
        building.get_building_type_id(),
    ]

    state = map_square.get_full_info()
    assert state == expected_state


def test_has_road_and_bridge(map_square):
    """
    Test checking for the presence of roads and bridges.
    """

    road = Road(map_square.position, 2)
    bridge = Bridge(map_square.position, 4)
    farm = Farm(0, map_square.position, 8)

    assert map_square.has_road() is False
    assert map_square.has_bridge() is False

    map_square.add_building(road)
    assert map_square.has_road() is True
    assert map_square.has_bridge() is False
    # Remove road
    map_square.remove_building(road)

    map_square.add_building(bridge)
    assert map_square.has_bridge() is True
    assert map_square.has_road() is False
    # Remove bridge
    map_square.remove_building(bridge)

    # test if farm is not a road or bridge
    map_square.add_building(farm)
    assert map_square.has_road() is False
    assert map_square.has_bridge() is False
