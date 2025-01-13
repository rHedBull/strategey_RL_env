import json

import pytest

from strategyRLEnv.environment import MapEnvironment
from strategyRLEnv.map.map_settings import OWNER_DEFAULT_TILE, BuildingType
from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.objects.City import City
from strategyRLEnv.objects.Road import Bridge, Road


@pytest.fixture
def setup():
    # open settings file
    with open("test_env_settings.json", "r") as f:
        env_settings = json.load(f)
        env_settings["map_width"] = 10
        env_settings["map_height"] = 10
        env_settings["actions"]["build_road"]["cost"] = 10

    agent_id = 0
    pos_x = 2
    pos_y = 2
    position_1 = MapPosition(pos_x, pos_y)
    position_2 = MapPosition(pos_x + 1, pos_y)

    mock_city_params = {
        "building_type_id": 1,
        "money_gain_per_turn": 110,
        "maintenance_cost_per_turn": 10,
    }
    city = City(agent_id, position_2, mock_city_params)
    action = [7, position_1.x, position_1.y]

    env = MapEnvironment(env_settings, 2, "rgb_array", seed=100)
    yield env, city, agent_id, position_1, position_2, action
    env.close()


def test_destroy_building_other_owner(setup):
    env, city, agent_id, position_1, position_2, destroy_action = setup
    env.reset()

    tile1 = env.map.get_tile(position_1)
    env.map.add_building(city, position_1)
    tile1.owner_id = 4

    # test building, owned by another agent, should not work
    observation, reward, terminated, truncated, info = env.step([[destroy_action]])
    assert tile1.has_building(BuildingType.CITY)
    assert tile1.owner_id == 4
    assert (
        observation["map"][3][position_1.x][position_1.y] == city.get_building_type_id()
    )


def test_destroy_own_building(setup):
    env, city, agent_id, position_1, position_2, destroy_action = setup
    env.reset()

    tile1 = env.map.get_tile(position_1)
    env.map.set_visible(position_1, agent_id)
    tile1.add_building(city)
    tile1.owner_id = agent_id

    # should work
    observation, reward, terminated, truncated, info = env.step([[destroy_action]])
    assert not tile1.has_building(BuildingType.CITY)
    assert tile1.get_owner() == agent_id
    assert observation["map"][3][position_1.x][position_1.y] == -1


def test_destroy_visible_road(setup):
    env, city, agent_id, position_1, position_2, destroy_action = setup
    env.reset()

    tile1 = env.map.get_tile(position_1)
    tile2 = env.map.get_tile(position_2)
    env.map.set_visible(position_1, agent_id)

    road = Road(position_1, {})
    tile1.add_building(road)

    # should work
    observation, reward, terminated, truncated, info = env.step([[destroy_action]])
    assert not tile1.has_building(BuildingType.ROAD)
    assert tile1.get_owner() == OWNER_DEFAULT_TILE
    assert observation["map"][3][position_1.x][position_1.y] == -1
