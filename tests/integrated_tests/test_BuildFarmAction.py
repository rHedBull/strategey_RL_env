import json

import pytest

from strategyRLEnv.environment import MapEnvironment
from strategyRLEnv.map.map_settings import LandType, BuildingType
from strategyRLEnv.map.MapPosition import MapPosition


@pytest.fixture
def setup():
    # open settings file
    with open("test_env_settings.json", "r") as f:
        env_settings = json.load(f)
        env_settings["map_width"] = 100
        env_settings["map_height"] = 100
    env_settings["actions"]["build_road"]["cost"] = 10  # allow building road
    env = MapEnvironment(env_settings, 2, "rgb_array")

    agent_id = 0
    pos_x = 2
    pos_y = 2
    position_1 = MapPosition(pos_x, pos_y)
    position_2 = MapPosition(pos_x + 1, pos_y)

    yield env, agent_id, position_1, position_2
    env.close()


def test_build_simple_farm(setup):
    env, agent_id, position_1, position_2 = setup
    env.reset()

    other_agent_id = 3
    build_farm_action = [5, position_1.x, position_1.y]
    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)

    # no visibility, should not work
    observation, reward, terminated, truncated, info = env.step([[build_farm_action]])
    assert tile1.has_any_building() is False

    # set visible
    env.map.set_visible(position_1, agent_id)
    # visible but unclaimed, should not work now
    observation, reward, terminated, truncated, info = env.step([[build_farm_action]])
    assert tile1.has_any_building() is False

    # claimed by another agent
    tile1.owner_id = other_agent_id  # claimed by another agent
    # visible but claimed by other agent, should not work now
    observation, reward, terminated, truncated, info = env.step([[build_farm_action]])
    assert tile1.has_any_building() is False

    # set tile claimed, should work
    tile1.owner_id = agent_id
    observation, reward, terminated, truncated, info = env.step([[build_farm_action]])
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.FARM) is True
    assert tile1.owner_id == agent_id

    # test build on top of existing building, should not work
    observation, reward, terminated, truncated, info = env.step([[build_farm_action]])
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.FARM) is True
    assert tile1.owner_id == agent_id
    # check that the building is still the same!!


def test_building_farm_on_water_mountain_desert(setup):
    env, agent_id, position_1, position_2 = setup
    build_farm_action = [5, position_1.x, position_1.y]

    # test all water
    with open("test_env_settings.json", "r") as f:
        env_settings = json.load(f)

    env_settings["map_width"] = 10
    env_settings["map_height"] = 10
    env_settings["actions"]["build_road"]["cost"] = 10  # allow building road

    special_env = MapEnvironment(env_settings, 2, "rgb_array")
    special_env.reset()
    agent_id = 0

    tile1 = special_env.map.get_tile(position_1)
    # set visible and claimed
    special_env.map.set_visible(position_1, agent_id)
    tile1.owner_id = agent_id

    # should not work on ocean
    tile1.set_land_type(LandType.OCEAN)
    observation, reward, terminated, truncated, info = special_env.step(
        [[build_farm_action]]
    )
    assert tile1.has_any_building() is False

    # should not work on mountain
    tile1.set_land_type(LandType.MOUNTAIN)
    observation, reward, terminated, truncated, info = special_env.step(
        [[build_farm_action]]
    )
    assert tile1.has_any_building() is False

    # should not work on dessert
    tile1.set_land_type(LandType.DESERT)
    observation, reward, terminated, truncated, info = special_env.step(
        [[build_farm_action]]
    )
    assert tile1.has_any_building() is False

    # should work on marsh
    tile1.set_land_type(LandType.MARSH)
    observation, reward, terminated, truncated, info = special_env.step(
        [[build_farm_action]]
    )
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.FARM) is True
