import json

import pytest

from map.map_settings import OWNER_DEFAULT_TILE, LandType
from rl_env.environment import MapEnvironment
from rl_env.objects.Building import BuildingType
from rl_env.objects.city import City


@pytest.fixture
def setup():
    # open settings file
    with open("test_env_settings.json", "r") as f:
        env_settings = json.load(f)

    env = MapEnvironment(env_settings, 2, "rgb_array")
    agent_id = 0
    pos_x = 2
    pos_y = 2
    city = City(agent_id, (pos_x + 1, pos_y), 1)
    yield env, city, agent_id, pos_x, pos_y
    env.close()


def test_build_simple_city(setup):
    env, city, agent_id, pos_x, pos_y = setup

    env.reset()
    other_agent_id = 3
    pos_x = 2
    pos_y = 2
    agent_id = 0
    build_city_action = [1, pos_x, pos_y]
    tile1 = env.map.get_tile((pos_x, pos_y))

    # no visibility, should not work
    observation, reward, terminated, truncated, info = env.step([[build_city_action]])
    assert tile1.has_any_building() is False

    # set visible and unclaimed
    env.map.set_visible((pos_x, pos_y), agent_id)
    tile1.owner_id = other_agent_id  # claimed by another agent

    # visible but claimed by other agent, should not work now
    observation, reward, terminated, truncated, info = env.step([[build_city_action]])
    assert tile1.has_any_building() is False

    # set tile unclaimed,
    tile1.owner_id = OWNER_DEFAULT_TILE
    observation, reward, terminated, truncated, info = env.step([[build_city_action]])
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.CITY) is True
    assert tile1.owner_id == agent_id

    # test build on top of existing building, should not work
    observation, reward, terminated, truncated, info = env.step([[build_city_action]])
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.CITY) is True
    assert tile1.owner_id == agent_id
    # check that the building is still the same!!


def test_building_city_on_water_mountain_desert(setup):
    env, city, agent_id, pos_x, pos_y = setup

    build_city_action = [1, pos_x, pos_y]

    # test all water
    with open("test_env_settings.json", "r") as f:
        env_settings = json.load(f)
    env_settings["actions"]["build_road"]["cost"] = 10  # allow building road

    special_env = MapEnvironment(env_settings, 2, "rgb_array")
    special_env.reset()

    # set visible
    special_env.map.set_visible((pos_x, pos_y), agent_id)
    tile1 = special_env.map.get_tile((pos_x, pos_y))

    # should not work on ocean
    tile1.set_land_type(LandType.OCEAN)
    observation, reward, terminated, truncated, info = special_env.step(
        [[build_city_action]]
    )
    assert tile1.has_any_building() is False

    # should not work on mountain
    tile1.set_land_type(LandType.MOUNTAIN)
    observation, reward, terminated, truncated, info = special_env.step(
        [[build_city_action]]
    )
    assert tile1.has_any_building() is False

    # should work on dessert
    tile1.set_land_type(LandType.DESERT)
    observation, reward, terminated, truncated, info = special_env.step(
        [[build_city_action]]
    )
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.CITY) is True

    tile1.buildings = set()
    tile1.building_int = 0
    tile1.owner_id = OWNER_DEFAULT_TILE

    # should work on marsh
    tile1.set_land_type(LandType.MARSH)
    observation, reward, terminated, truncated, info = special_env.step(
        [[build_city_action]]
    )
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.CITY) is True
