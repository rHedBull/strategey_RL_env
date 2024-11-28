import json

import pytest

from map.map_settings import LandType
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
    city = City(agent_id, (pos_x + 1, pos_y), 1)

    yield env, city, agent_id, pos_x, pos_y
    env.close()


def test_build_simple_farm(setup):
    env, city, agent_id, pos_x, pos_y = setup
    env.reset()

    other_agent_id = 3
    build_farm_action = [4, pos_x, pos_y]
    tile1 = env.map.get_tile((pos_x, pos_y))

    # test build without visibility, should not work
    observation, reward, terminated, truncated, info = env.step(
        [[ build_farm_action]]
    )
    assert tile1.has_any_building() is False

    # set visible and claimed
    env.map.set_visible((pos_x, pos_y), agent_id)
    tile1.owner_id = other_agent_id # claimed by another agent

    # should not work now
    observation, reward, terminated, truncated, info = env.step(
        [[build_farm_action]]
    )
    assert tile1.has_any_building() is False

    # set tile claimed, should work
    tile1.owner_id = agent_id
    observation, reward, terminated, truncated, info = env.step(
        [[build_farm_action]]
    )
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.FARM) is True
    assert tile1.owner_id == agent_id

    # test build on top of existing building, should not work
    observation, reward, terminated, truncated, info = env.step(
        [[build_farm_action]]
    )
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.FARM) is True
    assert tile1.owner_id == agent_id
    # check that the building is still the same!!


def test_building_farm_on_water_mountain_desert(setup):
    env, city, agent_id, pos_x, pos_y = setup
    build_farm_action = [4, pos_x, pos_y]

    # test all water
    with open("test_env_settings.json", "r") as f:
        env_settings = json.load(f)

    env_settings["map_width"] = 10
    env_settings["map_height"] = 10
    env_settings["actions"]["build_road"]["cost"] = 10  # allow building road

    special_env = MapEnvironment(env_settings, 2, "rgb_array")
    special_env.reset()
    agent_id = 0

    # set visible
    special_env.map.set_visible((pos_x, pos_y), agent_id)
    tile1 = special_env.map.get_tile((pos_x, pos_y))
    tile2 = special_env.map.get_tile((pos_x + 1, pos_y + 1))

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
