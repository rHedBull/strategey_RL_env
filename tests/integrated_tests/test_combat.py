import json

import pytest

from strategyRLEnv.environment import MapEnvironment
from strategyRLEnv.map.map_settings import LandType
from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.objects.City import City
from strategyRLEnv.objects.Unit import Unit


@pytest.fixture
def setup():
    # open settings file
    with open("test_env_settings.json", "r") as f:
        env_settings = json.load(f)
        env_settings["map_width"] = 10
        env_settings["map_height"] = 10
        env_settings["actions"]["build_road"]["cost"] = 10
        env_settings["mountain_budget_per_agent"] = 0.0
        env_settings["water_budget_per_agent"] = 0.0

    pos_x = 2
    pos_y = 2
    position_1 = MapPosition(pos_x, pos_y)
    position_2 = MapPosition(pos_x + 1, pos_y)

    env = MapEnvironment(env_settings, 2, "rgb_array", seed=100)
    env.reset()
    agent = env.agents[0]
    opp = env.agents[1]
    unit = Unit(agent, position_1)
    opponent = Unit(opp, position_2)
    agent.add_unit(unit)
    opp.add_unit(opponent)
    yield env, unit, opponent, position_1, position_2
    env.close()


# with opponent
# test one unit, one opponent, same strength
# test one unit, one opponent, 1 stronger, verify damage
# test unit 3 times stronger, wins immediately
# test unit kills other unit


def test_one_unit_one_opponent_same_strength(setup):
    """
    1) # no opponent
    Place a unit on a visible, empty LAND tile. Should succeed.
    """
    env, unit, opponent, position_1, position_2 = setup

    # place unit and opponent next to each other
    env.map.set_visible(position_1, agent_id=unit.owner.id)
    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    env.map.add_unit(unit, position_1)

    tile2 = env.map.get_tile(position_2)
    tile2.set_land_type(LandType.LAND)
    env.map.add_unit(opponent, position_2)

    wait_action = [0, position_2.x, position_2.y]

    # Step once
    observation, reward, terminated, truncated, info = env.step([[wait_action]])

    # Assert both units, should have lost no strength
    assert tile1.unit is not None, "Tile should have a unit after valid placement."
    assert tile1.unit.owner.id == unit.owner.id, "Placed unit should belong to agent 0."
    assert tile1.unit.strength < 50, "Unit should still have 50 strength."

    assert tile2.unit is not None, "Tile should have a unit after valid placement."
    assert (
        tile2.unit.owner.id == opponent.owner.id
    ), "Placed unit should belong to agent 1."
    assert tile2.unit.strength < 50, "Unit should still have 50 strength."

    assert (
        tile2.unit.strength == tile1.unit.strength
    ), "Equal opponents should receive same damage."
    assert env.map.unit_strength_map[position_2.x][position_2.y] == tile2.unit.strength
    assert env.map.unit_strength_map[position_1.x][position_1.y] == tile1.unit.strength


def test_one_unit_one_opponent_not_same_strength(setup):
    """
    1) # no opponent
    Place a unit on a visible, empty LAND tile. Should succeed.
    """
    env, unit, opponent, position_1, position_2 = setup

    # place unit and opponent next to each other
    env.map.set_visible(position_1, agent_id=unit.owner.id)
    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    unit.strength = 100
    env.agents[0].add_unit(unit)
    env.map.add_unit(unit, position_1)

    tile2 = env.map.get_tile(position_2)
    tile2.set_land_type(LandType.LAND)
    env.agents[1].add_unit(opponent)
    opponent.strength = 80
    env.map.add_unit(opponent, position_2)

    wait_action = [0, position_2.x, position_2.y]

    # Step once
    observation, reward, terminated, truncated, info = env.step([[wait_action]])

    # Assert both units, should have lost  strength
    assert tile1.unit.strength < 100, "Attacker should have lost strength."
    assert tile2.unit.strength < 80, "Opponent should have lost strength."

    diff_1 = 100 - tile1.unit.strength
    diff_2 = 80 - tile2.unit.strength

    assert (
        diff_1 < diff_2
    ), "stronger unit should have lost less strength than opponent."

    assert tile1.unit is not None, "Tile should have a unit after valid placement."
    assert tile1.unit.owner.id == unit.owner.id, "Placed unit should belong to agent 0."

    assert tile2.unit is not None, "Tile should have a unit after valid placement."
    assert (
        tile2.unit.owner.id == opponent.owner.id
    ), "Placed unit should belong to agent 1."


def test_unit_kills_other_unit(setup):
    """
    16) # with opponent
    Test that once a unit's strength <= 0, it is killed and removed from the map.
    Example: Attacker's big strength vs small strength = normal kill scenario.
    """
    env, unit, opponent, position_1, position_2 = setup

    unit.strength = 90
    opponent.strength = 30

    env.map.add_unit(unit, position_1)
    env.map.add_unit(opponent, position_2)

    unit.step(env)

    # Attack again
    # unit.step(env)

    assert opponent.strength <= 0, "Opponent should be killed on first hit."
    assert env.map.get_tile(position_2).unit is None, "Tile no longer has the opponent."
    assert (
        env.map.unit_strength_map[position_2.x][position_2.y] == 0
    ), "Unit strength should be 0"

    # attacker should still be damaged
    assert unit.strength < 90
    assert env.map.unit_strength_map[position_1.x][position_1.y] == unit.strength


def test_attack_on_city(setup):
    env, unit, opponent, position_1, position_2 = setup

    city = City(opponent.owner, position_2, {})
    city.health = 10
    tile2 = env.map.get_tile(position_2)
    tile2.add_building(city)

    wait_action = [0, position_2.x, position_2.y]

    # Step once, unit should destroy the city
    observation, reward, terminated, truncated, info = env.step([[wait_action]])

    assert tile2.has_any_building() is False
    assert observation["map"][3][position_1.x][position_1.y] == -1
