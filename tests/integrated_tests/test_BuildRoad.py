import json

import pytest

from strategyRLEnv.environment import MapEnvironment
from strategyRLEnv.map.map_settings import (OWNER_DEFAULT_TILE, BuildingType,
                                            LandType)
from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.objects.City import City
from strategyRLEnv.objects.Farm import Farm
from strategyRLEnv.objects.Mine import Mine
from strategyRLEnv.objects.Road import Bridge, Road


@pytest.fixture
def setup():
    # open settings file
    with open("test_env_settings.json", "r") as f:
        env_settings = json.load(f)
        env_settings["map_width"] = 10
        env_settings["map_height"] = 10
    env_settings["actions"]["build_road"]["cost"] = 10  # allow building road
    env = MapEnvironment(env_settings, 2, "rgb_array")
    env.reset()

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
    yield env, city, agent_id, position_1, position_2

    env.close()


def test_build_road_not_visible(setup):
    env, _, agent_id, position_1, _ = setup
    build_road_action = [3, position_1.x, position_1.y]

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    env.map.clear_visible(position_1, agent_id)

    # Not visible, should not work
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert (
        not tile1.has_any_building()
    ), "Building should not be placed on non-visible tile"


def test_build_bridge_not_visible(setup):
    env, _, agent_id, position_1, _ = setup
    build_bridge_action = [4, position_1.x, position_1.y]

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.OCEAN)

    # Not visible, should not work
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert (
        not tile1.has_any_building()
    ), "Building should not be placed on non-visible tile"


def test_build_road_claimed_by_other(setup):
    env, _, agent_id, position_1, _ = setup
    build_road_action = [3, position_1.x, position_1.y]

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    env.map.set_visible(position_1, agent_id)
    tile1.owner_id = 3  # Claimed by another agent

    # Visible but claimed by another agent, should not work
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert (
        not tile1.has_any_building()
    ), "Building should not be placed on tile claimed by another agent"


def test_build_bridge_claimed_by_other(setup):
    env, _, agent_id, position_1, _ = setup
    build_bridge_action = [4, position_1.x, position_1.y]

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    env.map.set_visible(position_1, agent_id)
    tile1.owner_id = 3  # Claimed by another agent

    # Visible but claimed by another agent, should not work
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert (
        not tile1.has_any_building()
    ), "Building should not be placed on tile claimed by another agent"


def test_build_road_claimed_by_self(setup):
    env, _, agent_id, position_1, _ = setup
    build_road_action = [3, position_1.x, position_1.y]

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    env.map.set_visible(position_1, agent_id)
    tile1.owner_id = agent_id  # Claimed by self

    # Visible and claimed by self, should work
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert not tile1.has_building(
        BuildingType.ROAD
    ), "Building should not be placed on self-owned tile"


def test_build_bridge_claimed_by_self(setup):
    env, _, agent_id, position_1, _ = setup
    build_bridge_action = [4, position_1.x, position_1.y]

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    env.map.set_visible(position_1, agent_id)
    tile1.owner_id = agent_id  # Claimed by self

    # Visible and claimed by self, should work
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert not tile1.has_building(
        BuildingType.BRIDGE
    ), "Building should not be placed on self-owned tile"


def test_build_road_unclaimed_no_adjacent(setup):
    env, _, agent_id, position_1, _ = setup
    build_road_action = [3, position_1.x, position_1.y]

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    env.map.set_visible(position_1, agent_id)
    tile1.owner_id = OWNER_DEFAULT_TILE  # Unclaimed

    # Visible, unclaimed, but no adjacent buildings, should not work
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert (
        not tile1.has_any_building()
    ), "Should not build road on unclaimed tile with no adjacent buildings"


def test_build_bridge_unclaimed_no_adjacent(setup):
    env, _, agent_id, position_1, _ = setup
    build_bridge_action = [4, position_1.x, position_1.y]

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    env.map.set_visible(position_1, agent_id)
    tile1.owner_id = OWNER_DEFAULT_TILE  # Unclaimed

    # Visible, unclaimed, but no adjacent buildings, should not work
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert (
        not tile1.has_any_building()
    ), "Should not build road on unclaimed tile with no adjacent buildings"


def test_build_road_next_to_hostile_city(setup):
    env, city, agent_id, position_1, position_2 = setup
    build_road_action = [3, position_1.x, position_1.y]

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    env.map.set_visible(position_1, agent_id)
    tile1.owner_id = OWNER_DEFAULT_TILE  # Unclaimed

    # Add opponent city next to tile1
    tile2 = env.map.get_tile(position_2)
    tile2.add_building(city)
    tile2.owner_id = 7  # Opponent agent

    # Next to a hostile city, should not work
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert not tile1.has_any_building(), "Should not build road next to hostile city"


def test_build_bridge_next_to_hostile_city(setup):
    env, city, agent_id, position_1, position_2 = setup
    build_bridge_action = [4, position_1.x, position_1.y]

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.OCEAN)
    env.map.set_visible(position_1, agent_id)
    tile1.owner_id = OWNER_DEFAULT_TILE  # Unclaimed

    # Add opponent city next to tile1
    tile2 = env.map.get_tile(position_2)
    tile2.add_building(city)
    tile2.owner_id = 7  # Opponent agent

    # Next to a hostile city, should not work
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert not tile1.has_any_building(), "Should not build road next to hostile city"


def test_build_road_next_to_friendly_city(setup):
    env, city, agent_id, position_1, position_2 = setup
    build_road_action = [3, position_1.x, position_1.y]

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    env.map.set_visible(position_1, agent_id)
    tile1.owner_id = OWNER_DEFAULT_TILE  # Unclaimed

    # Add friendly city next to tile1
    tile2 = env.map.get_tile(position_2)
    tile2.add_building(city)
    tile2.owner_id = agent_id  # Friendly agent

    # Next to a friendly city, should work
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert tile1.has_building(
        BuildingType.ROAD
    ), "Should build road next to friendly city"


def test_build_bridge_next_to_friendly_city(setup):
    env, city, agent_id, position_1, position_2 = setup
    build_bridge_action = [4, position_1.x, position_1.y]

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.OCEAN)
    env.map.set_visible(position_1, agent_id)
    tile1.owner_id = OWNER_DEFAULT_TILE  # Unclaimed

    # Add friendly city next to tile1
    tile2 = env.map.get_tile(position_2)
    tile2.add_building(city)
    tile2.owner_id = agent_id  # Friendly agent

    # Next to a friendly city, should work
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert tile1.has_building(
        BuildingType.BRIDGE
    ), "Should build bridge next to friendly city"


def test_build_road_next_to_road(setup):
    env, _, agent_id, position_1, position_2 = setup
    build_road_action = [3, position_1.x, position_1.y]

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    env.map.set_visible(position_1, agent_id)

    # Build bridge on tile2
    road = Road(position_2, {"building_type_id": 2})
    tile2 = env.map.get_tile(position_2)
    tile2.set_land_type(LandType.LAND)
    tile2.add_building(road)

    # Build road next to bridge, should work
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert tile1.has_building(BuildingType.ROAD), "Should build road next to bridge"


def test_build_bridge_next_to_bridge(setup):
    env, _, agent_id, position_1, position_2 = setup
    build_bridge_action = [4, position_1.x, position_1.y]

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.OCEAN)
    env.map.set_visible(position_1, agent_id)

    # Build road on tile2
    bridge = Bridge(position_2, {"building_type_id": 3})
    tile2 = env.map.get_tile(position_2)
    tile2.set_land_type(LandType.OCEAN)
    tile2.add_building(bridge)

    # Build bridge next to road, should work
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert tile1.has_building(BuildingType.BRIDGE), "Should build bridge next to road"


def test_build_road_next_to_bridge(setup):
    env, _, agent_id, position_1, position_2 = setup
    build_road_action = [3, position_1.x, position_1.y]

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)
    env.map.set_visible(position_1, agent_id)

    # Build bridge on tile2
    bridge = Bridge(position_2, {"building_type_id": 3})
    tile2 = env.map.get_tile(position_2)
    tile2.set_land_type(LandType.OCEAN)
    tile2.add_building(bridge)

    # Build road next to bridge, should work
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert tile1.has_building(BuildingType.ROAD), "Should build road next to bridge"


def test_build_bridge_next_to_road(setup):
    env, _, agent_id, position_1, position_2 = setup
    build_bridge_action = [4, position_1.x, position_1.y]

    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.OCEAN)
    env.map.set_visible(position_1, agent_id)

    # Build road on tile2
    road = Road(position_2, {"building_type_id": 3})
    tile2 = env.map.get_tile(position_2)
    tile2.set_land_type(LandType.LAND)
    tile2.add_building(road)

    # Build bridge next to road, should work
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert tile1.has_building(BuildingType.BRIDGE), "Should build bridge next to road"


def test_road_bridge_multiplier(setup):
    env, city, agent_id, position_1, position_2 = setup

    mine = Mine(
        agent_id, position_2, {"building_type_id": 5, "money_gain_per_turn": 100}
    )
    income = mine.get_income()
    tile2 = env.map.get_tile(position_2)
    tile2.add_building(mine)
    tile2.owner_id = agent_id
    build_road_action = [3, position_1.x, position_1.y]
    build_bridge_action = [4, position_1.x, position_1.y]
    tile1 = env.map.get_tile(position_1)
    position_3 = MapPosition(position_1.x, position_1.y + 1)
    tile3 = env.map.get_tile(position_3)
    tile3.add_building(city)
    tile3.owner_id = agent_id

    assert tile2.has_building(BuildingType.MINE) is True
    # build road next to mine
    env.map.set_visible(position_1, agent_id)
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert mine.get_income() > income

    # remove road
    env.map.remove_building(position_1, BuildingType.ROAD)
    assert tile1.has_any_building() is False
    assert mine.get_income() == income

    # build bridge next to mine
    tile1.set_land_type(LandType.OCEAN)
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert mine.get_income() > income
    env.map.remove_building(position_1, BuildingType.BRIDGE)
    tile2.remove_building(BuildingType.MINE)

    # same for farm
    env.map.remove_building(position_1, BuildingType.MINE)
    farm = Farm(
        agent_id, position_2, {"building_type_id": 4, "money_gain_per_turn": 100}
    )
    farm_income = farm.get_income()
    tile2.add_building(farm)

    # build road next to farm
    tile1.set_land_type(LandType.LAND)
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert farm.get_income() > farm_income

    # remove road
    env.map.remove_building(position_1, BuildingType.ROAD)
    assert farm.get_income() == farm_income

    # build bridge next to farm
    tile1.set_land_type(LandType.OCEAN)
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert farm.get_income() > farm_income


def test_building_road_on_water_mountain_desert(setup):
    env, city, agent_id, position_1, position_2 = setup
    build_road_action = [3, position_1.x, position_1.y]

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
    tile2 = special_env.map.get_tile(position_2)
    tile2.add_building(city)
    tile2.owner_id = agent_id

    # should not work on ocean
    tile1.set_land_type(LandType.OCEAN)
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
    tile1.remove_building(BuildingType.ROAD)
    assert tile1.has_any_building() is False

    # should work on marsh
    tile1.set_land_type(LandType.MARSH)
    special_env.map.set_visible(
        MapPosition(position_1.x + 1, position_1.y + 1), agent_id
    )
    observation, reward, terminated, truncated, info = special_env.step(
        [[build_road_action]]
    )
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.ROAD) is True

    tile1.remove_building(BuildingType.ROAD)

    # should work on mountain
    tile1.set_land_type(LandType.MOUNTAIN)
    observation, reward, terminated, truncated, info = special_env.step(
        [[build_road_action]]
    )
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.ROAD) is True
    env.close()


def test_building_bridge_on_water_mountain_desert(setup):
    env, city, agent_id, position_1, position_2 = setup

    build_bridge_action = [4, position_1.x, position_1.y]

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
    tile2 = special_env.map.get_tile(position_2)
    tile2.add_building(city)
    tile2.owner_id = agent_id
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
    env.close()
