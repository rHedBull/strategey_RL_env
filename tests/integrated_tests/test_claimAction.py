import json

import pytest

from strategyRLEnv.environment import MapEnvironment
from strategyRLEnv.map.map_settings import OWNER_DEFAULT_TILE
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

    pos_x = 2
    pos_y = 2
    position_1 = MapPosition(pos_x, pos_y)
    position_2 = MapPosition(pos_x + 1, pos_y)

    env = MapEnvironment(env_settings, 2, "rgb_array", seed=100)
    agent_0 = env.agents[0]
    city = City(agent_0, position_2, {})
    env.reset()
    tile1 = env.map.get_tile(position_1)
    tile2 = env.map.get_tile(position_2)
    claim_action = [1, position_1.x, position_1.y]
    yield env, city, agent_0, position_1, position_2, tile1, tile2, claim_action
    env.close()


def test_claim_without_visibility(setup):
    env, city, agent_0, position_1, position_2, tile1, tile2, claim_action = setup
    env.map.clear_visible(position_1, agent_0.id)
    observation, reward, terminated, truncated, info = env.step([[claim_action]])
    assert tile1.get_owner() == OWNER_DEFAULT_TILE
    assert env.map.ownership_map[position_1.x, position_1.y] == OWNER_DEFAULT_TILE


def test_claim_with_visibility(setup):
    env, city, agent_0, position_1, position_2, tile1, tile2, claim_action = setup

    # set visible and adjacent tile claimed
    env.map.set_visible(position_1, agent_0.id)
    # set adjacent tile to be claimed by agent
    tile2.owner_id = agent_0.id

    # should work now
    observation, reward, terminated, truncated, info = env.step([[claim_action]])
    assert tile1.get_owner() == agent_0.id
    assert env.map.ownership_map[position_1.x, position_1.y] == agent_0.id


def test_claiming_self_owned_tile(setup):
    env, city, agent_0, position_1, position_2, tile1, tile2, claim_action = setup
    tile1.owner_id = agent_0.id
    env.map.ownership_map[position_1.x, position_1.y] = agent_0.id
    env.map.set_visible(position_1, agent_0.id)

    # if we already own the tile, nothing should change
    observation, reward, terminated, truncated, info = env.step([[claim_action]])
    assert tile1.get_owner() == agent_0.id
    assert env.map.ownership_map[position_1.x, position_1.y] == agent_0.id


def test_claiming_no_adjacent_tile(setup):
    env, city, agent_0, position_1, position_2, tile1, tile2, claim_action = setup
    env.map.set_visible(position_1, agent_0.id)
    tile1.owner_id = OWNER_DEFAULT_TILE  # set tile to be unclaimed
    road = Road(position_2, {})
    tile2.add_building(road)  # add city to adjacent tile
    tile2.owner_id = OWNER_DEFAULT_TILE  # road is not owned by anyone
    # visible, unclaimed, but only next to a road, should not work
    observation, reward, terminated, truncated, info = env.step([[claim_action]])
    assert tile1.get_owner() == OWNER_DEFAULT_TILE
    assert env.map.ownership_map[position_1.x, position_1.y] == OWNER_DEFAULT_TILE


def test_claiming_adjacent_city(setup):
    env, city, agent_0, position_1, position_2, tile1, tile2, claim_action = setup
    tile2.add_building(city)  # add city to adjacent tile
    tile2.owner_id = agent_0.id  # city is owned by agent
    env.map.set_visible(position_1, agent_0.id)
    # visible, unclaimed and next to a city, should work
    observation, reward, terminated, truncated, info = env.step([[claim_action]])
    assert tile1.get_owner() == agent_0.id
    assert env.map.ownership_map[position_1.x, position_1.y] == agent_0.id


def test_claiming_only_opponent_tiles_adjacent(setup):
    env, city, agent_0, position_1, position_2, tile1, tile2, claim_action = setup
    other_agent_id = 3
    tile2.owner_id = other_agent_id
    tile1.owner_id = OWNER_DEFAULT_TILE
    env.map.set_visible(position_1, agent_0.id)
    # adjacent tiles are claimed only by another agent, should not work
    observation, reward, terminated, truncated, info = env.step([[claim_action]])
    assert tile1.get_owner() == OWNER_DEFAULT_TILE
    assert env.map.ownership_map[position_1.x, position_1.y] == OWNER_DEFAULT_TILE


def test_claiming_opponent_tile(setup):
    env, city, agent_0, position_1, position_2, tile1, tile2, claim_action = setup
    other_agent_id = 3
    # tile is already claimed by another agent, should not work
    tile1.owner_id = other_agent_id
    env.map.ownership_map[position_1.x, position_1.y] = other_agent_id
    env.map.set_visible(position_1, agent_0.id)
    observation, reward, terminated, truncated, info = env.step([[claim_action]])
    assert tile1.get_owner() == other_agent_id
    assert env.map.ownership_map[position_1.x, position_1.y] == other_agent_id


def test_claiming_opponent_and_self_tiles_adjacent(setup):
    env, city, agent_0, position_1, position_2, tile1, tile2, claim_action = setup
    other_agent_id = 3
    tile2.owner_id = other_agent_id
    position_3 = MapPosition(
        position_1.x, position_1.y + 1
    )  # testing here if it works diagonally
    tile3 = env.map.get_tile(position_3)
    tile3.owner_id = agent_0.id
    tile1.owner_id = OWNER_DEFAULT_TILE
    env.map.set_visible(position_1, agent_0.id)
    # tile is unclaimed and adjacent tiles are claimed by another agent and self, should work
    observation, reward, terminated, truncated, info = env.step([[claim_action]])
    assert tile1.get_owner() == agent_0.id
    assert env.map.ownership_map[position_1.x, position_1.y] == agent_0.id
