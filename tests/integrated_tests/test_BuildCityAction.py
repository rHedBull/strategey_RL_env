import json

import pytest

from strategyRLEnv.environment import MapEnvironment
from strategyRLEnv.map.map_settings import (OWNER_DEFAULT_TILE, BuildingType,
                                            LandType)
from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.objects.City import City
from strategyRLEnv.objects.Unit import Unit
from tests.env_tests.test_action_manager import MockAgent


@pytest.fixture
def setup():
    # open settings file
    with open("test_env_settings.json", "r") as f:
        env_settings = json.load(f)
        env_settings["agent_water_budget"] = 0.0
        env_settings["agent_mountain_budget"] = 0.0
        env_settings["map_width"] = 100
        env_settings["map_height"] = 100

    env = MapEnvironment(env_settings, 2, "rgb_array")
    env.reset()
    agent_id = 0
    pos_x = 2
    pos_y = 2
    position_1 = MapPosition(pos_x, pos_y)
    position_2 = MapPosition(pos_x + 1, pos_y)
    build_city_action = [2, position_1.x, position_1.y]

    yield env, agent_id, position_1, position_2, build_city_action
    env.close()


def test_build_city_invisible_tile(setup):
    env, agent_id, position_1, position_2, build_city_action = setup

    env.reset()
    tile1 = env.map.get_tile(position_1)
    env.map.set_invisible(position_1, agent_id)

    # no visibility, should not work
    observation, reward, terminated, truncated, info = env.step([[build_city_action]])
    assert tile1.has_any_building() is False
    assert observation["map"][3][position_1.x][position_1.y] == -1


def test_build_city_other_claimed_tile(setup):
    env, agent_id, position_1, position_2, build_city_action = setup

    env.reset()
    tile1 = env.map.get_tile(position_1)
    env.map.set_visible(position_1, agent_id)
    tile1.owner_id = 3
    # visible but claimed by other agent, should not work now
    observation, reward, terminated, truncated, info = env.step([[build_city_action]])
    assert tile1.has_any_building() is False


def test_build_city_visible_unclaimed(setup):
    env, agent_id, position_1, position_2, build_city_action = setup

    env.reset()
    tile1 = env.map.get_tile(position_1)
    env.map.set_visible(position_1, agent_id)
    tile1.owner_id = OWNER_DEFAULT_TILE

    observation, reward, terminated, truncated, info = env.step([[build_city_action]])
    assert tile1.has_building(BuildingType.CITY) is True
    object = tile1.get_building()
    assert isinstance(object, City)
    assert object.position.x == position_1.x
    assert object.position.y == position_1.y
    assert env.agents[agent_id].cities[1] == object
    assert (
        observation["map"][3][position_1.x][position_1.y]
        == object.get_building_type_id()
    )


def test_build_city_on_existing_building(setup):
    env, agent_id, position_1, position_2, build_city_action = setup

    env.reset()
    tile1 = env.map.get_tile(position_1)
    env.map.set_visible(position_1, agent_id)
    tile1.owner_id = agent_id
    city = City(agent_id, position_1, {})
    old_id = city.id
    env.map.add_building(city, position_1)

    # test build on top of existing building, should not work
    observation, reward, terminated, truncated, info = env.step([[build_city_action]])
    assert tile1.has_building(BuildingType.CITY) is True
    assert tile1.owner_id == agent_id
    assert tile1.get_building().id == old_id, "City should not be replaced"
    assert observation["map"][3][position_1.x][position_1.y] == 0


def test_building_city_on_opponent_unit(setup):
    env, agent_id, position_1, position_2, build_city_action = setup

    env.reset()
    tile1 = env.map.get_tile(position_1)
    env.map.set_visible(position_1, agent_id)

    agent = MockAgent(id=3)
    unit = Unit(agent, position_1)

    tile1.unit = unit
    observation, reward, terminated, truncated, info = env.step([[build_city_action]])
    assert tile1.has_any_building() is False
    assert tile1.unit is unit


def test_building_city_on_own_unit(setup):
    env, agent_id, position_1, position_2, build_city_action = setup

    env.reset()
    tile1 = env.map.get_tile(position_1)
    env.map.set_visible(position_1, agent_id)

    agent = MockAgent(id=agent_id)
    unit = Unit(agent, position_1)
    tile1.unit = unit
    observation, reward, terminated, truncated, info = env.step([[build_city_action]])
    assert tile1.unit is unit
    assert tile1.has_building(BuildingType.CITY) is True
    assert observation["map"][3][position_1.x][position_1.y] == 0


def test_building_city_on_water(setup):
    env, agent_id, position_1, position_2, build_city_action = setup

    # set visible
    env.map.set_visible(position_1, agent_id)
    tile1 = env.map.get_tile(position_1)

    # should not work on ocean
    tile1.set_land_type(LandType.OCEAN)
    observation, reward, terminated, truncated, info = env.step([[build_city_action]])
    assert tile1.has_any_building() is False


def test_building_city_on_mountain(setup):
    env, agent_id, position_1, position_2, build_city_action = setup

    # set visible
    env.map.set_visible(position_1, agent_id)
    tile1 = env.map.get_tile(position_1)
    # should not work on mountain
    tile1.set_land_type(LandType.MOUNTAIN)
    observation, reward, terminated, truncated, info = env.step([[build_city_action]])
    assert tile1.has_any_building() is False


def test_building_city_on_dessert(setup):
    env, agent_id, position_1, position_2, build_city_action = setup

    # set visible
    env.map.set_visible(position_1, agent_id)
    tile1 = env.map.get_tile(position_1)

    tile1.set_land_type(LandType.DESERT)
    observation, reward, terminated, truncated, info = env.step([[build_city_action]])
    assert tile1.has_building(BuildingType.CITY) is True
    assert observation["map"][3][position_1.x][position_1.y] == 0


def test_building_city_on_marsh(setup):
    env, agent_id, position_1, position_2, build_city_action = setup

    # set visible
    env.map.set_visible(position_1, agent_id)
    tile1 = env.map.get_tile(position_1)

    tile1.set_land_type(LandType.MARSH)
    observation, reward, terminated, truncated, info = env.step([[build_city_action]])
    assert tile1.has_building(BuildingType.CITY) is True
    assert observation["map"][3][position_1.x][position_1.y] == 0
