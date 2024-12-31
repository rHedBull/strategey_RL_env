import json

import pytest

from strategyRLEnv.environment import MapEnvironment
from strategyRLEnv.map.map_settings import OWNER_DEFAULT_TILE, LandType
from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.objects.Building import BuildingType
from strategyRLEnv.objects.City import City
from strategyRLEnv.objects.Farm import Farm
from strategyRLEnv.objects.Mine import Mine


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
    mock_city_params = {
        "building_type_id": 1,
        "money_gain_per_turn": 110,
        "maintenance_cost_per_turn": 10,
        "max_level": 3,
    }
    city = City(agent_id, position_2, mock_city_params)
    yield env, city, agent_id, position_1, position_2

    env.close()


def test_build_simple_road(setup):
    env, city, agent_id, position_1, position_2 = setup
    build_road_action = [3, position_1.x, position_1.y]

    env.reset()
    tile1 = env.map.get_tile(position_1)
    tile1.set_land_type(LandType.LAND)

    # not visible, should not work
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert tile1.has_any_building() is False

    # set visible and claimed by another agent
    env.map.set_visible(position_1, agent_id)
    tile1.owner_id = 3  # claimed by another agent

    # visible but claimed by another agent, should not work now
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert tile1.has_any_building() is False

    # set tile unclaimed,
    tile1.owner_id = agent_id

    # claimed and visible, should not work
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert tile1.has_any_building() is False

    # # test build on top of existing building, should not work
    # observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    # assert tile1.has_any_building() is True
    # assert tile1.has_building(BuildingType.ROAD) is True
    # check that the building is still the same!!

    # remove the road
    tile1.buildings = set()
    tile1.building_int = 0
    assert tile1.has_any_building() is False, "Road should be removed"

    # set tile unclaimed,
    tile1.owner_id = OWNER_DEFAULT_TILE
    # visible unclaimed but no building next to it, should not work
    # visible but claimed by another agent, should not work now
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert tile1.has_any_building() is False

    # add a opponent city next to it
    env.map.get_tile(position_2).add_building(city)
    tile2 = env.map.get_tile(position_2)
    tile2.owner_id = 7
    # next to a hostile city should not work
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert tile1.has_any_building() is False

    # next to a friendly city should work
    tile2.owner_id = agent_id
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.ROAD) is True

    # removing city on tile 2
    tile2.buildings = set()
    tile2.building_int = 0
    tile2.owner_id = OWNER_DEFAULT_TILE
    tile2.set_land_type(LandType.OCEAN)
    assert tile2.has_any_building() is False

    # test building bridge next to bridge
    observation, reward, terminated, truncated, info = env.step(
        [[[4, position_2.x, position_2.y]]]
    )
    assert tile2.has_any_building() is True
    assert tile2.has_building(BuildingType.BRIDGE) is True

    # test building bridge next to bridge
    tile2.buildings = set()
    tile2.building_int = 0
    tile2.set_land_type(LandType.LAND)
    observation, reward, terminated, truncated, info = env.step(
        [[[3, position_2.x, position_2.y]]]
    )
    assert tile2.has_any_building() is True
    assert tile2.has_building(BuildingType.ROAD) is True

    # removing roads on tile 2
    tile2.buildings = set()
    tile2.building_int = 0
    tile1.buildings = set()
    tile1.building_int = 0
    # place owned mine on tile 2
    mine = Farm(agent_id, position_2, {"building_type_id": 4})
    tile2.add_building(mine)
    tile2.owner_id = agent_id
    # next to self owned mine should not work
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert tile1.has_any_building() is False


def test_build_simple_bridge(setup):
    env, city, agent_id, position_1, position_2 = setup
    env.reset()

    build_bridge_action = [4, position_1.x, position_1.y]
    tile1 = env.map.get_tile(position_1)

    tile1.set_land_type(LandType.OCEAN)
    # not visible, should not work
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert tile1.has_any_building() is False

    # set visible and claimed by another agent
    env.map.set_visible(position_1, agent_id)
    tile1.owner_id = 3  # claimed by another agent

    # visible but claimed by another agent, should not work now
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert tile1.has_any_building() is False

    # set tile claimed,
    tile1.owner_id = agent_id

    # claimed and visible should not work
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert tile1.has_any_building() is False

    # test build on top of existing building, should not work
    # observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    # assert tile1.has_any_building() is True
    # assert tile1.has_building(BuildingType.BRIDGE) is True
    # check that the building is still the same!!

    # remove the road
    tile1.buildings = set()
    tile1.building_int = 0
    assert tile1.has_any_building() is False, "Bridge should be removed"

    # set tile unclaimed,
    tile1.owner_id = -1
    # visible unclaimed but no building next to it, should not work
    # visible but claimed by another agent, should not work now
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert tile1.has_any_building() is False

    # add an opponent city next to it
    env.map.get_tile(position_2).add_building(city)
    tile2 = env.map.get_tile(position_2)
    tile2.owner_id = 7
    # next to a hostile city should not work
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert tile1.has_any_building() is False

    # next to a friendly city should work
    tile2.owner_id = agent_id
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert tile1.has_any_building() is True
    assert tile1.has_building(BuildingType.BRIDGE) is True

    # removing city on tile 2
    tile2.buildings = set()
    tile2.building_int = 0
    tile2.owner_id = OWNER_DEFAULT_TILE
    tile2.set_land_type(LandType.LAND)
    assert tile2.has_any_building() is False

    # test building road next to bridge
    observation, reward, terminated, truncated, info = env.step(
        [[[3, position_2.x, position_2.y]]]
    )
    assert tile2.has_any_building() is True
    assert tile2.has_building(BuildingType.ROAD) is True

    # test building bridge next to bridge
    tile2.buildings = set()
    tile2.building_int = 0
    tile2.set_land_type(LandType.OCEAN)
    observation, reward, terminated, truncated, info = env.step(
        [[[4, position_2.x, position_2.y]]]
    )
    assert tile2.has_any_building() is True
    assert tile2.has_building(BuildingType.BRIDGE) is True

    # removing roads on tile 2
    tile2.buildings = set()
    tile2.building_int = 0
    tile1.buildings = set()
    tile1.building_int = 0
    # place owned mine on tile 2
    mine = Mine(agent_id, position_2, {"building_type_id": 5})
    tile2.add_building(mine)
    tile2.owner_id = agent_id
    # next to self owned mine should not work
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert tile1.has_any_building() is False


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
    tile1.buildings = set()
    tile1.building_int = 0
    assert mine.get_income() == income

    # build bridge next to mine
    observation, reward, terminated, truncated, info = env.step([[build_bridge_action]])
    assert mine.get_income() > income

    # same for farm
    tile2.buildings = set()
    tile2.building_int = 0
    farm = Farm(agent_id, position_2, {"building_type_id": 4})
    farm_income = farm.get_income()

    # build road next to farm
    observation, reward, terminated, truncated, info = env.step([[build_road_action]])
    assert farm.get_income() > farm_income

    # remove road
    tile1.buildings = set()
    tile1.building_int = 0
    assert farm.get_income() == farm_income

    # build bridge next to farm
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

    tile1.building_int = 0
    tile1.buildings = set()
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

    tile1.building_int = 0
    tile1.buildings = set()

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
