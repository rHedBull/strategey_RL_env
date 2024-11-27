import json

import pytest

from agents.Sim_Agent import Agent
from map.map_settings import OWNER_DEFAULT_TILE, LandType
from map.map_square import Map_Square
from map.sim_map import Map, check_valid_agent_id, max_agent_id
from rl_env.environment import MapEnvironment
from rl_env.objects.city import City


class MockAgent:
    pass  # Simplified Agent class


@pytest.fixture
def map_instance():
    """Fixture to create and return a Map instance."""

    # open settings file
    with open("test_env_settings.json", "r") as f:
        env_settings = json.load(f)

    env = MapEnvironment(env_settings, 2, "rgb_array")

    m = Map(env)
    return m


def test_check_valid_agent_id():
    # Test valid IDs
    assert check_valid_agent_id(0) is True
    assert check_valid_agent_id(max_agent_id - 1) is True

    # Test invalid IDs
    assert check_valid_agent_id(-1) is False
    assert check_valid_agent_id(max_agent_id) is False
    assert check_valid_agent_id(100) is False


def test_map_initialization(map_instance):
    assert map_instance.width == 100
    assert map_instance.height == 100
    assert map_instance.water_percentage == 0.0
    assert map_instance.mountain_percentage == 0.0
    assert map_instance.dessert_percentage == 0.0
    assert map_instance.rivers == 0
    assert map_instance.resource_density == 0.1
    # assert map_instance.biomes_definition == {}
    # assert map_instance.land_resource_definition == {}
    # assert (
    #    map_instance.sea_resource_definition == {}
    # )


def test_create_map(map_instance):
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
    for row in map_instance.squares:
        for square in row:
            assert square.land_type == LandType.LAND

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
    # Valid positions
    assert map_instance.check_position_on_map((0, 0)) is True
    assert map_instance.check_position_on_map((99, 99)) is True
    assert map_instance.check_position_on_map((54, 50)) is True

    # Invalid positions
    assert map_instance.check_position_on_map((-1, 0)) is False
    assert map_instance.check_position_on_map((0, -1)) is False
    assert map_instance.check_position_on_map((100, 100)) is False
    assert map_instance.check_position_on_map((100, 5)) is False
    assert map_instance.check_position_on_map((5, 100)) is False


def test_get_tile(map_instance):
    # Valid tile
    tile = map_instance.get_tile((5, 5))
    assert tile is not None
    assert tile.x == 5
    assert tile.y == 5

    tile = map_instance.get_tile((0, 0))
    assert tile is not None
    assert tile.x == 0
    assert tile.y == 0

    tile = map_instance.get_tile((99, 99))
    assert tile is not None
    assert tile.x == 99
    assert tile.y == 99

    # Invalid tile
    tile = map_instance.get_tile((100, 100))
    assert tile is None
    tile = map_instance.get_tile((-1, 0))
    assert tile is None
    tile = map_instance.get_tile((0, -1))
    assert tile is None


def test_visibility_methods(map_instance):
    position = (3, 9)
    agent_id = 10  # Valid agent ID
    agent_id2 = 3

    # Initially not visible
    assert not map_instance.is_visible(position, agent_id)
    assert not map_instance.is_visible(position, agent_id2)

    # Set visible
    map_instance.set_visible(position, agent_id)
    assert map_instance.is_visible(position, agent_id)
    assert not map_instance.is_visible(position, agent_id2)

    # Set visible for another agent
    map_instance.set_visible(position, agent_id2)
    assert map_instance.is_visible(position, agent_id)
    assert map_instance.is_visible(position, agent_id2)

    # Clear visible
    map_instance.clear_visible(position, agent_id)
    assert not map_instance.is_visible(position, agent_id)
    assert map_instance.is_visible(position, agent_id2)

    # Test with invalid agent ID
    invalid_agent_id = max_agent_id
    map_instance.set_visible(position, invalid_agent_id)  # Should have no effect
    assert map_instance.is_visible(position, agent_id2)
    assert not map_instance.is_visible(position, invalid_agent_id)

    map_instance.clear_visible(position, invalid_agent_id)  # Should have no effect
    assert map_instance.is_visible(position, agent_id2)
    assert not map_instance.is_visible(position, invalid_agent_id)

    map_instance.clear_visible(position, agent_id2)
    assert not map_instance.is_visible(position, agent_id2)


def test_claim_tile(map_instance):
    position = (2, 4)
    mock_agent = Agent(7, None)  # Using a mock agent
    tile = map_instance.get_tile(position)

    assert tile.owner_id == OWNER_DEFAULT_TILE  # Initially unclaimed
    map_instance.claim_tile(mock_agent, position)
    assert tile.owner_id == mock_agent.id


def test_add_building(map_instance):
    position = (2, 4)
    building_object = City(1, position, 1)  # Mock building object
    tile = map_instance.get_tile(position)

    assert not tile.has_any_building()
    map_instance.add_building(building_object, position)
    assert tile.has_any_building()
    assert building_object in tile.buildings


def test_tile_is_next_to_building(map_instance):
    position = (3, 5)
    adjacent_position = (4, 5)

    # Initially, no buildings nearby
    assert map_instance.tile_is_next_to_building(adjacent_position) is False

    building_object = City(1, position, 1)
    map_instance.add_building(building_object, position)

    # Now, should detect a building nearby
    assert map_instance.tile_is_next_to_building(adjacent_position) is True


def test_serialize_topography_resources(map_instance):
    map_instance.reset()  # Ensure map is in a known state

    map_data = map_instance.serialize_topography_resources()

    assert map_data["width"] == map_instance.width
    assert map_data["height"] == map_instance.height
    assert "squares" in map_data
    assert len(map_data["squares"]) == map_instance.height
    assert len(map_data["squares"][0]) == map_instance.width


def test_save_and_load_topography_resources(map_instance, tmp_path):
    map_instance.reset()
    file_path = tmp_path / "map_data.pkl"

    # Save the map
    map_instance.save_topography_resources(str(file_path))
    assert file_path.exists()

    # Create a new map instance and load the data

    new_map = Map(map_instance.env)
    new_map.load_topography_resources(str(file_path), map_instance.env.env_settings)

    assert new_map.width == map_instance.width
    assert new_map.height == map_instance.height
    assert len(new_map.squares) == new_map.height
    assert len(new_map.squares[0]) == new_map.width

    # Compare some squares
    for y in range(new_map.height):
        for x in range(new_map.width):
            original_square = map_instance.get_tile((x, y))
            loaded_square = new_map.get_tile((x, y))
            assert loaded_square.tile_id == original_square.tile_id
            assert loaded_square.x == original_square.x
            assert loaded_square.y == original_square.y
            assert loaded_square.land_type == original_square.land_type
            # assert loaded_square.resources == original_square.resources
