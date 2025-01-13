import json

import pytest

from strategyRLEnv.Agent import Agent
from strategyRLEnv.environment import MapEnvironment
from strategyRLEnv.map.map_settings import LandType
from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.objects.City import City
from strategyRLEnv.objects.Farm import Farm
from strategyRLEnv.objects.Road import Road
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

    agent_id = 0
    pos_x = 2
    pos_y = 2
    position_1 = MapPosition(pos_x, pos_y)
    position_2 = MapPosition(pos_x + 1, pos_y)

    env = MapEnvironment(env_settings, 2, "rgb_array", seed=100)
    agent = Agent(agent_id, env)
    opp = Agent(1, env)
    unit = Unit(agent, position_1)
    opponent = Unit(opp, position_2)
    yield env, unit, opponent, position_1, position_2
    env.close()


def test_place_unit_on_visible_land_tile(setup):
    """
    1) # no opponent
    Place a unit on a visible, empty LAND tile. Should succeed.
    """
    env, unit, opponent, position_1, position_2 = setup
    env.reset()

    # Make sure position_1 is visible and land
    env.map.set_visible(position_1, agent_id=unit.owner.id)
    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)

    # place_unit action for agent 0
    place_unit_action = [8, position_1.x, position_1.y]

    # Step once
    observation, reward, terminated, truncated, info = env.step([[place_unit_action]])
    tile1 = env.map.get_tile(position_1)

    # Assert the tile now has a unit belonging to agent 0
    assert tile1.unit is not None, "Tile should have a unit after valid placement."
    assert tile1.unit.owner.id == unit.owner.id, "Placed unit should belong to agent 0."
    assert (
        env.map.unit_strength_map[position_1.x][position_1.y] == unit.strength
    ), "Unit strength should be on map"


def test_place_unit_on_friendly_unit(setup):
    """
    1) # no opponent
    Place a unit on a visible, empty LAND tile. Should succeed.
    """
    env, unit, opponent, position_1, position_2 = setup
    env.reset()

    # Make sure position_1 is visible and land
    env.map.set_visible(position_1, agent_id=unit.owner.id)
    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    tile1.unit = unit
    tile1.unit.strength = 50
    env.agents[0].units.append(unit)

    # place_unit action for agent 0
    place_unit_action = [8, position_1.x, position_1.y]

    # Step once
    observation, reward, terminated, truncated, info = env.step([[place_unit_action]])
    tile1 = env.map.get_tile(position_1)

    # Assert the tile now has a unit belonging to agent 0
    assert tile1.unit is not None, "Tile should have a unit after valid placement."
    assert tile1.unit.owner.id == unit.owner.id, "Placed unit should belong to agent 0."
    assert (
        tile1.unit.strength == 100
    ), "Unit should add 50 to the already exisiting 50 strength."
    assert (
        env.map.unit_strength_map[position_1.x][position_1.y] == unit.strength
    ), "Unit strength should be on map"


def test_place_unit_on_invisible(setup):
    """
    2) # no opponent
    If the tile is not visible to the agent, placing a unit fails."""
    env, unit, opponent, position_1, position_2 = setup
    env.reset()

    # Ensure position_1 is not visible
    env.map.clear_visible(position_1, agent_id=unit.owner.id)
    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)

    place_unit_action = [8, position_1.x, position_1.y]

    observation, reward, terminated, truncated, info = env.step([[place_unit_action]])
    assert tile1.unit is None, "Tile should not have a unit if invisible."
    assert (
        env.map.unit_strength_map[position_1.x][position_1.y] == 0
    ), "Unit strength should still be 0"


def test_place_unit_on_enemy_claimed_tile_2support(setup):
    """
    3) # no opponent
    Place a unit on a tile owned by the opponent,
    but only if it's not fully surrounded by enemy territory.
    """
    # assuming conquer_threshold = 2
    env, unit, opponent, position_1, position_2 = setup
    env.reset()

    # Mark position_1 as enemy territory
    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    tile1.owner_id = opponent.owner.id  # Owned by agent 1
    env.map.ownership_map[position_1.x, position_1.y] = opponent.owner.id

    # place 2 friendly unit around position_1
    tile2 = env.map.get_tile(position_2)
    tile2.unit = unit
    tile3 = env.map.get_tile(MapPosition(position_1.x + 1, position_1.y + 1))
    tile3.unit = unit
    env.map.ownership_map[position_2.x, position_2.y] = unit.owner.id
    env.map.ownership_map[position_1.x + 1, position_1.y + 1] = unit.owner.id
    env.map.set_visible(position_1, agent_id=unit.owner.id)

    place_unit_action = [8, position_1.x, position_1.y]

    # Step
    observation, reward, terminated, truncated, info = env.step([[place_unit_action]])

    assert (
        tile1.unit is not None
    ), "Unit should be placed on not-fully-surrounded enemy tile."
    assert tile1.unit.owner.id == unit.owner.id, "Now tile1 should have agent 0's unit."
    assert tile1.owner_id == unit.owner.id, "Tile should now belong to agent 0."
    assert (
        env.map.ownership_map[position_1.x, position_1.y] == unit.owner.id
    ), "Ownership map should reflect the change."
    assert (
        env.map.unit_strength_map[position_1.x, position_1.y] == unit.strength
    ), "Unit strength should be on map"


def test_place_unit_on_enemy_claimed_tile_1support(setup):
    """
    3) # no opponent
    Place a unit on a tile owned by the opponent,
    but only if it's not fully surrounded by enemy territory.
    """
    # assuming conquer_threshold = 2
    env, unit, opponent, position_1, position_2 = setup
    env.reset()

    # Mark position_1 as enemy territory
    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    tile1.owner_id = opponent.owner.id  # Owned by agent 1

    # place only 1 friendly unit around position_1
    tile2 = env.map.get_tile(position_2)
    tile2.unit = unit
    env.map.set_visible(position_1, agent_id=unit.owner.id)

    place_unit_action = [8, position_1.x, position_1.y]

    # Step
    observation, reward, terminated, truncated, info = env.step([[place_unit_action]])

    assert (
        tile1.unit is None
    ), "Unit should not be placed on fully-surrounded enemy tile."
    assert tile1.owner_id == opponent.owner.id, "Tile should still belong to opponent."


def test_place_unit_on_own_tile(setup):
    """
    4) # no opponent
    Place a unit on your own tile.
    """
    env, unit, opponent, position_1, position_2 = setup
    env.reset()

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    tile1.owner_id = unit.owner.id
    env.map.set_visible(position_1, agent_id=unit.owner.id)

    place_unit_action = [8, position_1.x, position_1.y]

    observation, reward, terminated, truncated, info = env.step([[place_unit_action]])

    assert tile1.unit is not None, "Tile should have the newly placed unit."
    assert (
        tile1.unit.owner.id == unit.owner.id
    ), "Placed unit belongs to the correct agent."


def test_place_unit_on_enemy_unit(setup):
    """
    5) # no opponent
    Attempt to place a unit on a an enemy unit.
    Often triggers combat or is disallowed. We'll demonstrate a conflict scenario.
    """
    env, unit, opponent, position_1, position_2 = setup
    env.reset()

    opponent.strength = 77
    tile2 = env.map.get_tile(position_2)
    tile2.set_land_type(LandType.LAND)
    env.map.add_unit(opponent, position_2)

    # Make sure agent 0 sees that tile
    env.map.set_visible(position_2, agent_id=unit.owner.id)

    place_unit_action = [8, position_2.x, position_2.y]

    observation, reward, terminated, truncated, info = env.step([[place_unit_action]])
    assert tile2.unit is not None, "Tile should still have the enemy unit."
    assert (
        tile2.unit.owner.id == opponent.owner.id
    ), "Enemy unit should remain on the tile."
    assert (
        env.map.unit_strength_map[position_2.x][position_2.y] == opponent.strength
    ), "oponent strength should not change"


def test_place_unit_on_ocean_fails(setup):
    """
    6) # no opponent
    Placing a unit on OCEAN tile might disallowed.
    """
    env, unit, opponent, position_1, position_2 = setup
    env.reset()

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.OCEAN)
    env.map.set_visible(position_1, agent_id=unit.owner.id)

    place_unit_action = [8, position_1.x, position_1.y]

    observation, reward, terminated, truncated, info = env.step([[place_unit_action]])

    # If disallowed, tile1.unit stays None
    assert tile1.unit is None, "Unit should not be placed on ocean tile."


def test_place_unit_on_mountain_fails(setup):
    """
    6) # no opponent
    Placing a unit on OCEAN tile might disallowed.
    """
    env, unit, opponent, position_1, position_2 = setup
    env.reset()

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.MOUNTAIN)
    env.map.set_visible(position_1, agent_id=unit.owner.id)

    place_unit_action = [8, position_1.x, position_1.y]

    observation, reward, terminated, truncated, info = env.step([[place_unit_action]])

    # If disallowed, tile1.unit stays None
    assert tile1.unit is None, "Unit should not be placed on mountain tile."


def test_place_unit_on_building_tile_allows_coexistence(setup):
    """
    8) # no opponent
    game allows a unit to stand on a tile with a building
    """
    env, unit, opponent, position_1, position_2 = setup
    env.reset()

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    env.map.set_visible(position_1, agent_id=unit.owner.id)

    # Suppose building_type_id=3 is some building
    city = City(unit.owner.id, position_1, {})
    farm = Farm(unit.owner.id, position_1, {})
    road = Road(position_1, {})

    # test with city
    tile1.add_building(city)
    place_unit_action = [8, position_1.x, position_1.y]
    observation, reward, terminated, truncated, info = env.step([[place_unit_action]])
    # Adjust depending on your rules
    assert tile1.unit is not None, "Unit should coexist with city."
    assert tile1.unit.owner.id == unit.owner.id, "Unit is owned by agent 0."
    tile1.remove_building()
    tile1.unit = None

    # test with road
    tile1.add_building(road)
    place_unit_action = [8, position_1.x, position_1.y]
    observation, reward, terminated, truncated, info = env.step([[place_unit_action]])
    # Adjust depending on your rules
    assert tile1.unit is not None, "Unit should coexist with city."
    assert tile1.unit.owner.id == unit.owner.id, "Unit is owned by agent 0."
    tile1.remove_building()
    tile1.unit = None

    # test with farm
    tile1.add_building(farm)
    place_unit_action = [8, position_1.x, position_1.y]
    observation, reward, terminated, truncated, info = env.step([[place_unit_action]])
    # Adjust depending on your rules
    assert tile1.unit is not None, "Unit should coexist with city."
    assert tile1.unit.owner.id == unit.owner.id, "Unit is owned by agent 0."


def test_remove_unit_action_empty_tile(setup):
    """
    11) # no opponent
    If your environment has a "remove/kill" action ID (e.g., 9),
    test that stepping with that action removes the unit from the tile.
    """
    env, unit, opponent, position_1, position_2 = setup
    env.reset()

    # First place the unit
    env.map.set_visible(position_1, agent_id=unit.owner.id)
    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    tile1.unit = None

    remove_unit_action = [9, position_1.x, position_1.y]

    obs, rew, term, trunc, info = env.step([[remove_unit_action]])

    assert tile1.unit is None, "Tile should have no unit after removal."
    assert (
        env.map.unit_strength_map[position_1.x][position_1.y] == 0
    ), "Unit strength should be 0"


def test_remove_unit_action_own_unit(setup):
    """
    11) # no opponent
    If your environment has a "remove/kill" action ID (e.g., 9),
    test that stepping with that action removes the unit from the tile.
    """
    env, unit, opponent, position_1, position_2 = setup
    env.reset()

    # First place the unit
    env.map.set_visible(position_1, agent_id=unit.owner.id)
    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    tile1.unit = unit

    remove_unit_action = [9, position_1.x, position_1.y]

    obs, rew, term, trunc, info = env.step([[remove_unit_action]])

    assert tile1.unit is None, "Tile should have no unit after removal."
    assert (
        unit not in env.agents[0].units
    ), "Unit should be removed from agent 0's list of units."
    assert (
        env.map.unit_strength_map[position_1.x][position_1.y] == 0
    ), "Unit strength should be 0"


def test_remove_enemy_unit(setup):
    """
    11) # no opponent
    If your environment has a "remove/kill" action ID (e.g., 9),
    test that stepping with that action removes the unit from the tile.
    """
    env, unit, opponent, position_1, position_2 = setup
    env.reset()

    # First place the unit
    env.map.set_visible(position_1, agent_id=unit.owner.id)
    tile2 = env.map.get_tile(position_2)
    tile2.set_land_type(LandType.LAND)
    env.map.add_unit(opponent, position_2)

    remove_unit_action = [9, position_2.x, position_2.y]

    obs, rew, term, trunc, info = env.step([[remove_unit_action]])

    assert tile2.unit is not None, "Tile should still have a unit after removal."
    assert (
        tile2.unit.owner.id == opponent.owner.id
    ), "Unit should still belong to agent 1."
    assert (
        env.map.unit_strength_map[position_2.x][position_2.y] == opponent.strength
    ), "Unit strength should be 0"
