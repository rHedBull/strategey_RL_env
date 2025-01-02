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

    agent_id = 0
    pos_x = 2
    pos_y = 2
    position_1 = MapPosition(pos_x, pos_y)
    position_2 = MapPosition(pos_x + 1, pos_y)

    mock_city_params = {
        "building_type_id": 1,
        "money_gain_per_turn": 110,
        "maintenance_cost_per_turn": 10,
        "max_level": 3,
    }
    city = City(agent_id, position_2, mock_city_params)

    env = MapEnvironment(env_settings, 2, "rgb_array", seed=100)
    yield env, city, agent_id, position_1, position_2
    env.close()


def test_simple_wait(setup):
    env, city, agent_id, position_1, position_2 = setup
    env.reset()

    wait_action = [0, position_1.x, position_1.y]
    tile1 = env.map.get_tile(position_1)
    tile2 = env.map.get_tile(position_2)

    # test build without visibility, should not work
    observation, reward, terminated, truncated, info = env.step([[wait_action]])
    assert tile1.get_owner() == OWNER_DEFAULT_TILE
    assert tile1.has_any_building() is False

    # set visible and adjacent tile claimed
    env.map.set_visible(position_1, agent_id)
    # set adjacent tile to be claimed by agent
    tile2.owner_id = agent_id

    # should always work, but change nothing
    observation, reward, terminated, truncated, info = env.step([[wait_action]])
    assert tile1.get_owner() == OWNER_DEFAULT_TILE
    assert tile1.has_any_building() is False

    # if we already own the tile, nothing should change
    tile1.owner_id = agent_id
    observation, reward, terminated, truncated, info = env.step([[wait_action]])
    assert tile1.get_owner() == agent_id
    assert tile1.has_any_building() is False

    road = Road(position_1, {"building_type_id": 2, "max_level": 3})
    tile1.add_building(road)  # add city to adjacent tile

    observation, reward, terminated, truncated, info = env.step([[wait_action]])
    assert tile1.get_owner() == agent_id
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.ROAD) is True
