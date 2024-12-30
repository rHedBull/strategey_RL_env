import json
import uuid

import pytest

from strategyRLEnv.Agent import Agent
from strategyRLEnv.environment import MapEnvironment
from strategyRLEnv.map.Map import check_valid_agent_id
from strategyRLEnv.map.map_settings import (OWNER_DEFAULT_TILE, LandType,
                                            max_agent_id)
from strategyRLEnv.map.mapGenerator import generate_finished_map
from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.map.MapSquare import Map_Square
from strategyRLEnv.objects.Building import BuildingType
from strategyRLEnv.objects.City import City
from strategyRLEnv.objects.Mine import Mine


class MockAgent:
    pass  # Simplified Agent class


@pytest.fixture
def map_instance():
    """Fixture to create and return a Map instance."""

    # open settings file
    with open("test_env_settings.json", "r") as f:
        env_settings = json.load(f)

    env = MapEnvironment(env_settings, 2, "rgb_array")

    map = generate_finished_map(env, env_settings)
    mock_city_params = {
        "building_type_id": 1,
        "money_gain_per_turn": 110,
        "maintenance_cost_per_turn": 10,
        "max_level": 3,
    }
    yield map, mock_city_params


def test_check_valid_agent_id():
    # Test valid IDs

    assert check_valid_agent_id(0) is True
    assert check_valid_agent_id(max_agent_id - 1) is True

    # Test invalid IDs
    assert check_valid_agent_id(-1) is False
    assert check_valid_agent_id(max_agent_id) is False
    assert check_valid_agent_id(100) is False


def test_map_initialization(map_instance):
    map_instance, mock_city_params = map_instance

    assert map_instance.env is not None
    assert isinstance(map_instance.id, uuid.UUID)
    assert map_instance.width == 100
    assert map_instance.height == 100
    assert map_instance.tiles == 10000


def test_create_map(map_instance):
    map_instance, mock_city_params = map_instance

    assert len(map_instance.squares) == map_instance.height
    for row in map_instance.squares:
        assert len(row) == map_instance.width
        for square in row:
            assert isinstance(square, Map_Square)
            assert square.land_type in [
                LandType.OCEAN,
                LandType.MOUNTAIN,
                LandType.DESERT,
                LandType.RIVER,
                LandType.MARSH,
                LandType.LAND,
            ]
            # assert square.resources == []
            assert square.buildings == set()
            # the rest should be tested in Map_Square tests


def test_reset(map_instance):
    # Before reset, squares should have default land type
    map_instance, mock_city_params = map_instance
    # for row in map_instance.squares:
    #     for square in row:
    #         assert square.land_type == LandType.LAND

    # Perform reset
    map_instance.reset()

    # After reset, verify land types based on the agents run
    # Since random walks are simplified, land types might remain OCEAN
    # Adjust assertions based on your agent's behavior
    for row in map_instance.squares:
        for square in row:
            # Example: Assuming some squares are set to MOUNTAIN, DESERT, or RIVER
            assert square.land_type in [
                LandType.OCEAN,
                LandType.MOUNTAIN,
                LandType.DESERT,
                LandType.RIVER,
                LandType.MARSH,
                LandType.LAND,
            ]


def test_check_position_on_map(map_instance):
    map_instance, mock_city_params = map_instance
    # Valid positions
    assert map_instance.check_position_on_map(MapPosition(0, 0)) is True
    assert map_instance.check_position_on_map(MapPosition(99, 99)) is True
    assert map_instance.check_position_on_map(MapPosition(54, 50)) is True

    # Invalid positions
    assert map_instance.check_position_on_map(MapPosition(-1, 0)) is False
    assert map_instance.check_position_on_map(MapPosition(0, -1)) is False
    assert map_instance.check_position_on_map(MapPosition(100, 100)) is False
    assert map_instance.check_position_on_map(MapPosition(100, 5)) is False
    assert map_instance.check_position_on_map(MapPosition(5, 100)) is False


def test_get_tile(map_instance):
    map_instance, mock_city_params = map_instance
    # Valid tile
    tile = map_instance.get_tile(MapPosition(5, 5))
    assert tile is not None
    assert tile.position.x == 5
    assert tile.position.y == 5

    tile = map_instance.get_tile(MapPosition(0, 0))
    assert tile is not None
    assert tile.position.x == 0
    assert tile.position.y == 0

    tile = map_instance.get_tile(MapPosition(99, 99))
    assert tile is not None
    assert tile.position.x == 99
    assert tile.position.y == 99

    # Invalid tile
    tile = map_instance.get_tile(MapPosition(100, 100))
    assert tile is None
    tile = map_instance.get_tile(MapPosition(-1, 0))
    assert tile is None
    tile = map_instance.get_tile(MapPosition(0, -1))
    assert tile is None


def test_visibility_methods(map_instance):
    position = MapPosition(3, 5)
    agent_id = 10  # Valid agent ID
    agent_id2 = 3

    map_instance, mock_city_params = map_instance
    # Initially not visible
    # check if of type bool
    assert isinstance(map_instance.is_visible(position, agent_id), bool)
    assert map_instance.is_visible(position, agent_id) is False
    assert map_instance.is_visible(position, agent_id2) is False

    # Set visible
    map_instance.set_visible(position, agent_id)
    assert map_instance.is_visible(position, agent_id) is True
    assert map_instance.is_visible(position, agent_id2) is False

    # Set visible for another agent
    map_instance.set_visible(position, agent_id2)
    assert map_instance.is_visible(position, agent_id) is True
    assert map_instance.is_visible(position, agent_id2) is True

    # Clear visible
    map_instance.clear_visible(position, agent_id)
    assert map_instance.is_visible(position, agent_id) is False
    assert map_instance.is_visible(position, agent_id2) is True

    # Test with invalid agent ID
    invalid_agent_id = max_agent_id
    map_instance.set_visible(position, invalid_agent_id)  # Should have no effect
    assert map_instance.is_visible(position, agent_id2) is True
    assert map_instance.is_visible(position, invalid_agent_id) is False

    map_instance.clear_visible(position, invalid_agent_id)  # Should have no effect
    assert map_instance.is_visible(position, agent_id2) is True
    assert map_instance.is_visible(position, invalid_agent_id) is False

    map_instance.clear_visible(position, agent_id2)
    assert map_instance.is_visible(position, agent_id2) is False


def test_claim_tile(map_instance):
    position = MapPosition(2, 4)
    map_instance, mock_city_params = map_instance
    mock_agent = Agent(7, map_instance.env)  # Using a mock agent
    tile = map_instance.get_tile(position)

    assert tile.owner_id == OWNER_DEFAULT_TILE  # Initially unclaimed
    map_instance.claim_tile(mock_agent, position)
    assert tile.owner_id == mock_agent.id

    # TODO: test here what happens at conflict claiming


def test_add_building(map_instance):
    position = MapPosition(2, 4)
    map_instance, mock_city_params = map_instance
    building_object = City(1, position, mock_city_params)  # Mock building object
    tile = map_instance.get_tile(position)

    assert tile.has_any_building() is False
    map_instance.add_building(building_object, position)
    assert tile.has_any_building() is True
    assert building_object in tile.buildings

    # test remove building
    tile.remove_building(building_object)
    assert tile.has_any_building() is False
    assert building_object not in tile.buildings


# def test_tile_is_next_to_building(map_instance):
#     position = MapPosition(3, 5)
#     adjacent_position = MapPosition(4, 5)
#     map_instance, mock_city_params = map_instance
#
#     # Initially, no buildings nearby
#     bool_value, return_tile = map_instance.tile_is_next_to_building(adjacent_position)
#     assert bool_value is False
#     assert return_tile is None
#
#     building_object = City(1, position, mock_city_params)
#     map_instance.add_building(building_object, position)
#
#     # Now, should detect a building nearby
#     tile = map_instance.get_tile(position)
#     bool_value, return_tile = map_instance.tile_is_next_to_building(adjacent_position)
#     assert bool_value is True
#     assert return_tile == tile

def test_tile_is_next_to_building_type(map_instance):
    position = MapPosition(3, 5)
    adjacent_position = MapPosition(4, 5)
    map_instance, mock_city_params = map_instance

    # Initially, no buildings nearby
    bool_value, return_tile = map_instance.tile_is_next_to_building_type(adjacent_position, BuildingType.CITY)
    assert bool_value is False
    assert return_tile is None

    # place city adjacent to position
    building_object = City(1, position, mock_city_params)
    map_instance.add_building(building_object, position)

    # check for a mine, should return false
    bool_value, return_tile = map_instance.tile_is_next_to_building_type(adjacent_position, BuildingType.MINE)
    assert bool_value is False
    assert return_tile is None

    tile = map_instance.get_tile(position)
    # now check for a city, should return true
    bool_value, return_tile = map_instance.tile_is_next_to_building(adjacent_position)
    assert bool_value is True
    assert return_tile == tile


def test_tile_is_next_to_any_building(map_instance):
    position = MapPosition(3, 5)
    adjacent_position = MapPosition(4, 5)
    position3 = MapPosition(3, 6)
    map_instance, mock_city_params = map_instance

    # Initially, no buildings nearby
    bool_value, return_tile = map_instance.tile_is_next_to_any_building(adjacent_position)
    assert bool_value is False
    assert return_tile is None

    building_object = City(1, position, mock_city_params)
    map_instance.add_building(building_object, position)

    # Now, should detect a building nearby
    tile = map_instance.get_tile(position)
    bool_value, return_tile = map_instance.tile_is_next_to_building(adjacent_position)
    assert bool_value is True
    assert return_tile == tile

    # now add a mine
    building_2 = Mine(7, position3, {"building_type_id": 5})
    tile3 = map_instance.get_tile(position3)
    map_instance.add_building(building_2, position3)
    # should still return true
    bool_value, return_tile = map_instance.tile_is_next_to_any_building(adjacent_position)
    assert bool_value is True

def test_tile_is_next_to_own_tile(map_instance):
    position = MapPosition(3, 5)
    adjacent_position = MapPosition(4, 5)
    position3 = MapPosition(3, 6)
    map_instance, mock_city_params = map_instance

    # Initially all unclaimed, should return false
    bool_value, return_tile = map_instance.tile_is_next_to_own_tile(adjacent_position, agent_id=1)
    assert bool_value is False
    assert return_tile is None

    # claim neighbouring tile with other agent
    tile1 = map_instance.get_tile(position)
    tile1.owner_id = 3

    # check if tile is next to own tile, should return false
    bool_value, return_tile = map_instance.tile_is_next_to_own_tile(adjacent_position, agent_id=1)

    tile1.owner_id = 1
    # now should return true
    bool_value, return_tile = map_instance.tile_is_next_to_own_tile(adjacent_position, agent_id=1)
    assert bool_value is True
    assert return_tile == tile1

    tile3 = map_instance.get_tile(position3)
    tile3.owner_id = 4
    # should still return true
    bool_value, return_tile = map_instance.tile_is_next_to_own_tile(adjacent_position, agent_id=1)
    assert bool_value is True
    assert return_tile == tile1
    # and also for 4
    bool_value, return_tile = map_instance.tile_is_next_to_own_tile(adjacent_position, agent_id=4)
    assert bool_value is True
    assert return_tile == tile3




def test_get_surrounding_tiles(map_instance):
    map_instance, mock_city_params = map_instance
    map_instance.reset()  # Ensure map is in a known state

    # Test Case 1: Middle position
    middle_position = MapPosition(2, 2)
    expected_positions = [
        (1, 1),
        (2, 1),
        (3, 1),
        (1, 2),
        (3, 2),
        (1, 3),
        (2, 3),
        (3, 3),
    ]
    surrounding_tiles = map_instance.get_surrounding_tiles(middle_position, 1)
    assert (
        len(surrounding_tiles) == len(expected_positions)
    ), "Middle position should have 8 surrounding tiles."
    for tile in surrounding_tiles:
        tile_position = (tile.position.x, tile.position.y)
        assert (
            tile_position in expected_positions
        ), f"Tile:({tile.position.x}, {tile.position.y}) not expected in middle position surroundings."

    # test with radius 2
    expected_positions2 = [
        (0, 0),
        (1, 0),
        (2, 0),
        (3, 0),
        (4, 0),
        (0, 1),
        (1,1),
        (2,1),
        (3,1),
        (4,1),
        (0,2),
        (1,2),
        (3,2),
        (4,2),
        (0,3),
        (1,3),
        (2,3),
        (3,3),
        (4,3),
        (0,4),
        (1,4),
        (2,4),
        (3,4),
        (4,4)
    ]

    surrounding_tiles = map_instance.get_surrounding_tiles(middle_position, 2)
    assert (
        len(surrounding_tiles) == len(expected_positions2)
    ), "Middle position should have 24 surrounding tiles."
    for tile in surrounding_tiles:
        tile_position = (tile.position.x, tile.position.y)
        assert (
            tile_position in expected_positions2
        ), f"Tile:({tile.position.x}, {tile.position.y}) not expected in middle position surroundings."

    expected_positions1_no_diagonal = [(2,1), (3,2), (2,3), (1,2)]
    surrounding_tiles = map_instance.get_surrounding_tiles(middle_position, 1, diagonal=False)
    assert (
            len(surrounding_tiles) == len(expected_positions1_no_diagonal)
    ), "Middle position should have 24 surrounding tiles."
    for tile in surrounding_tiles:
        tile_position = (tile.position.x, tile.position.y)
        assert (
                tile_position in expected_positions1_no_diagonal
        ), f"Tile:({tile.position.x}, {tile.position.y}) not expected in middle position surroundings."

    # Test Case 2: Corner position
    corner_position = MapPosition(0, 0)
    expected_positions = [(1, 0), (0, 1), (1, 1)]
    surrounding_tiles = map_instance.get_surrounding_tiles(corner_position, 1)
    assert (
        len(surrounding_tiles) == len(expected_positions)
    ), "Corner position should have 3 surrounding tiles (some may be out of bounds)."
    for tile in surrounding_tiles:
        tile_position = (tile.position.x, tile.position.y)
        assert (
            tile_position in expected_positions
        ), f"Tile ({tile.position.x}, {tile.position.y}) not expected in corner position surroundings."


    expected_positions2 = [(1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)]
    surrounding_tiles = map_instance.get_surrounding_tiles(corner_position, 2)
    assert (
            len(surrounding_tiles) == len(expected_positions2)
    ), "Corner position should have 8 surrounding tiles."
    for tile in surrounding_tiles:
        tile_position = (tile.position.x, tile.position.y)
        assert (
                tile_position in expected_positions2
        ), f"Tile ({tile.position.x}, {tile.position.y}) not expected in corner position surroundings."

    surrounding_tiles = map_instance.get_surrounding_tiles(corner_position, 2, diagonal=False)
    expected_positions2_no_diagonal = [(1, 0), (2, 0), (0, 1), (0, 2)]
    assert (
            len(surrounding_tiles) == len(expected_positions2_no_diagonal)
    ), "Corner position should have 4 surrounding tiles."
    for tile in surrounding_tiles:
        tile_position = (tile.position.x, tile.position.y)
        assert (
            tile_position in expected_positions2_no_diagonal
        ), f"Tile ({tile.position.x}, {tile.position.y}) not expected in corner position surroundings."


    # Test Case 3: Edge position
    edge_position = MapPosition(2, 0)
    surrounding_tiles = map_instance.get_surrounding_tiles(edge_position, 1)
    expected_positions = [(1, 0), (3, 0), (1, 1), (2, 1), (3, 1)]
    assert (
        len(surrounding_tiles) == len(expected_positions)
    ), "Edge position should have 5 surrounding tiles (some may be out of bounds)."
    for tile in surrounding_tiles:
        tile_position = (tile.position.x, tile.position.y)
        assert (
            tile_position in expected_positions
        ), f"Tile ({tile.position.x}, {tile.position.y}) not expected in edge position surroundings."

    expected_positions1_no_diagonal = [(1, 0), (3, 0), (2, 1)]
    surrounding_tiles = map_instance.get_surrounding_tiles(edge_position, 1, diagonal=False)
    assert (
        len(surrounding_tiles) == len(expected_positions1_no_diagonal)
    ), "Edge position without diagonals should have 3 surrounding tiles (some may be out of bounds)."
    for tile in surrounding_tiles:
        tile_position = (tile.position.x, tile.position.y)
        assert (
            tile_position in expected_positions1_no_diagonal
        ), f"Tile ({tile.position.x}, {tile.position.y}) not expected in edge position surroundings."

