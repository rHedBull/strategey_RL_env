import json

import pytest

from MapPosition import MapPosition
from map.map_settings import OWNER_DEFAULT_TILE, LandType
from rl_env.environment import MapEnvironment
from rl_env.objects.Building import BuildingType
from rl_env.objects.city import City


@pytest.fixture
def setup():
    # open settings file
    with open("test_env_settings.json", "r") as f:
        env_settings = json.load(f)
        env_settings["map_width"] = 10
        env_settings["map_height"] = 10
    env_settings["actions"]["build_road"]["cost"] = 10  # allow building road
    env = MapEnvironment(env_settings, 2, "rgb_array")

    agent_id = 0
    pos_x = 2
    pos_y = 2
    position_1 = MapPosition(pos_x, pos_y)
    position_2 = MapPosition(pos_x + 1, pos_y)
    city = City(agent_id, position_2, 1)
    yield env, city, agent_id, position_1, position_2

    env.close()


def test_build_simple_road(setup):
    env, city, agent_id, position_1, position_2 = setup
    build_road_action = [2, position_1.x, position_1.y]

    env.reset()
    tile1 = env.map.get_tile(position_1)

    # not visible, should not work
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert tile1.has_any_building() is False

    # set visible and claimed by another agent
    env.map.set_visible(position_1, agent_id)
    tile1.owner_id = 3  # claimed by another agent

    # visible but claimed by another agent, should not work now
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert tile1.has_any_building() is False

    # set tile unclaimed,
    tile1.owner_id = agent_id

    # claimed and visible, should work
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert tile1.has_any_building() is True
    assert (
        tile1.has_building(BuildingType.ROAD) is True
    ), "Road should be built on visible and self claimed tile"
    assert (
        tile1.get_owner() != OWNER_DEFAULT_TILE
    ), "Bulding a road should not claim the tile"

    # test build on top of existing building, should not work
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.ROAD) is True
    # check that the building is still the same!!

    # remove the road
    tile1.buildings = set()
    tile1.building_int = 0
    assert tile1.has_any_building() is False, "Road should be removed"

    # set tile unclaimed,
    tile1.owner_id = OWNER_DEFAULT_TILE
    # visible unclaimed but no building next to it, should not work
    # visible but claimed by another agent, should not work now
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert tile1.has_any_building() is False

    # add a city next to it
    env.map.get_tile(position_2).add_building(city)
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.ROAD) is True


def test_build_simple_bridge(setup):
    env, city, agent_id, position_1, position_2 = setup
    env.reset()

    build_bridge_action = [3, position_1.x, position_1.y]
    tile1 = env.map.get_tile(position_1)

    tile1.set_land_type(LandType.OCEAN)
    # not visible, should not work
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert tile1.has_any_building() is False

    # set visible and claimed by another agent
    env.map.set_visible(position_1, agent_id)
    tile1.owner_id = 3  # claimed by another agent

    # visible but claimed by another agent, should not work now
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert tile1.has_any_building() is False

    # set tile claimed,
    tile1.owner_id = agent_id

    # claimed and visible should work
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert tile1.has_any_building() is True
    assert (
        tile1.has_building(BuildingType.BRIDGE) is True
    ), "Bridge should be built on visible and self claimed tile"
    assert (
        tile1.get_owner() != OWNER_DEFAULT_TILE
    ), "Building a Bridge should not claim the tile"

    # test build on top of existing building, should not work
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.BRIDGE) is True
    # check that the building is still the same!!

    # remove the road
    tile1.buildings = set()
    tile1.building_int = 0
    assert tile1.has_any_building() is False, "Bridge should be removed"

    # set tile unclaimed,
    tile1.owner_id = -1
    # visible unclaimed but no building next to it, should not work
    # visible but claimed by another agent, should not work now
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert tile1.has_any_building() is False

    # add a city next to it
    env.map.get_tile(position_2).add_building(city)
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.BRIDGE) is True


def test_building_road_on_water_mountain_desert(setup):
    env, city, agent_id, position_1, position_2 = setup
    build_road_action = [2, position_1.x, position_1.y]

    # test all water
    with open("test_env_settings.json", "r") as f:
        env_settings = json.load(f)
    env_settings["actions"]["build_road"]["cost"] = 10  # allow building road
    env_settings["map_width"] = 10
    env_settings["map_height"] = 10

    special_env = MapEnvironment(env_settings, 2, "rgb_array")
    special_env.reset()
    agent_id = 0

    tile1 = special_env.map.get_tile(position_1)

    # set visible
    special_env.map.set_visible(position_1, agent_id)
    # set city next to it
    special_env.map.get_tile(position_2).add_building(city)

    # should not work on ocean
    tile1.set_land_type(LandType.OCEAN)
    observation, reward, terminated, truncated, info = special_env.step(
        [[build_road_action]]
    )
    assert tile1.has_any_building() is False

    # should not work on mountain
    tile1.set_land_type(LandType.MOUNTAIN)
    observation, reward, terminated, truncated, info = special_env.step(
        [[build_road_action]]
    )
    assert tile1.has_any_building() is False

    # should work on dessert
    tile1.set_land_type(LandType.DESERT)
    observation, reward, terminated, truncated, info = special_env.step(
        [[build_road_action]]
    )
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.ROAD) is True

    tile1.building_int = 0
    tile1.buildings = set()
    assert tile1.has_any_building() is False

    # should work on marsh
    tile1.set_land_type(LandType.MARSH)
    special_env.map.set_visible(MapPosition(position_1.x + 1, position_1.y + 1), agent_id)
    observation, reward, terminated, truncated, info = special_env.step(
        [[build_road_action]]
    )
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.ROAD) is True


def test_building_bridge_on_water_mountain_desert(setup):
    env, city, agent_id, position_1, position_2 = setup

    build_bridge_action = [3, position_1.x, position_1.y]

    # test all water
    with open("test_env_settings.json", "r") as f:
        env_settings = json.load(f)
    env_settings["actions"]["build_road"]["cost"] = 10  # allow building road
    env_settings["map_width"] = 10
    env_settings["map_height"] = 10

    special_env = MapEnvironment(env_settings, 2, "rgb_array")
    special_env.reset()

    tile1 = special_env.map.get_tile(position_1)

    # set visible
    special_env.map.set_visible(position_1, agent_id)
    # set city next to it
    special_env.map.get_tile(position_2).add_building(city)
    special_env.map.set_visible(position_1, agent_id)

    # should not work on mountain
    tile1.set_land_type(LandType.MOUNTAIN)
    observation, reward, terminated, truncated, info = special_env.step(
        [[build_bridge_action]]
    )
    assert tile1.has_any_building() is False

    # should not work on dessert
    tile1.set_land_type(LandType.DESERT)
    observation, reward, terminated, truncated, info = special_env.step(
        [[build_bridge_action]]
    )
    assert tile1.has_any_building() is False

    # should not work on marsh
    tile1.set_land_type(LandType.MARSH)

    observation, reward, terminated, truncated, info = special_env.step(
        [[build_bridge_action]]
    )
    assert tile1.has_any_building() is False

    # should work on ocean
    tile1.set_land_type(LandType.OCEAN)
    observation, reward, terminated, truncated, info = special_env.step(
        [[build_bridge_action]]
    )
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.BRIDGE) is True
