import json
import math
from unittest.mock import MagicMock

import pytest

from strategyRLEnv.Agent import (Agent, AgentState, calculate_new_position,
                                 get_visible_mask)
from strategyRLEnv.environment import MapEnvironment
from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.objects.City import City
from strategyRLEnv.objects.Unit import Unit


@pytest.fixture
def setup():
    agent_id = 0
    pos_x = 2
    pos_y = 2
    position_1 = MapPosition(pos_x, pos_y)
    position_2 = MapPosition(pos_x + 1, pos_y)

    city = City(agent_id, position_2, {})

    with open("test_env_settings.json", "r") as f:
        env_settings = json.load(f)
        env_settings["map_width"] = 10
        env_settings["map_height"] = 10

    env = MapEnvironment(env_settings, 2, "rgb_array")
    env.reset()
    yield env, city, agent_id, position_1, position_2
    env.close()


def test_get_visible_mask():
    agent_id = 2
    visibility_map = 0b10100  # Binary representation: agents 2 and 4 are visible
    mock_map_v = MagicMock()
    mock_map_v.visibility_map = visibility_map

    expected_visible = True  # Agent 2 is visible

    visible = get_visible_mask(agent_id, mock_map_v)
    assert visible == expected_visible

    # Test for an agent that is not visible
    agent_id = 1
    expected_visible = False
    visible = get_visible_mask(agent_id, mock_map_v)
    assert visible == expected_visible


def test_calculate_new_position():
    current_position = MapPosition(5, 5)

    # Test moving up
    new_position = calculate_new_position(current_position, 1)
    assert new_position.x == 5
    assert new_position.y == 4

    # Test moving down
    new_position = calculate_new_position(current_position, 2)
    assert new_position.x == 5
    assert new_position.y == 6

    # Test moving left
    new_position = calculate_new_position(current_position, 3)
    assert new_position.x == 4
    assert new_position.y == 5

    # Test moving right
    new_position = calculate_new_position(current_position, 4)
    assert new_position.x == 6
    assert new_position.y == 5

    # Test no move
    new_position = calculate_new_position(current_position, 0)
    assert new_position.x == 5
    assert new_position.y == 5

    # Test unrecognized direction
    new_position = calculate_new_position(current_position, 99)
    assert new_position.x == 5
    assert new_position.y == 5


def test_agent_initialization(setup):
    env, city, agent_id, position_1, position_2 = setup
    agent = env.agents[agent_id]

    assert agent.id == agent_id
    assert agent.state == AgentState.ACTIVE
    assert agent.money == env.env_settings["agent_initial_budget"]
    assert agent.visibility_range == 3
    assert agent.all_visible is False
    assert len(agent.cities) == 1
    assert len(agent.get_claimed_tiles()) == 1  # Only the starting position is claimed


def test_agent_update(setup):
    env, city, agent_id, position_1, position_2 = setup
    agent = env.agents[agent_id]

    initial_money = env.env_settings["agent_initial_budget"]
    assert agent.money == initial_money

    # Perform update
    agent.update()

    expected_money = initial_money
    assert agent.money == expected_money
    assert agent.last_money_pl == 0

    # Now, set money to a negative value to trigger kill
    agent.money = 48
    agent.reduce_money(50)
    assert agent.state == AgentState.DONE
    assert agent.id in env.done_agents


def test_agent_kill(setup):
    env, city, agent_id, position_1, position_2 = setup
    agent = env.agents[agent_id]

    unit1 = Unit(agent, position_1)
    unit2 = Unit(agent, position_2)
    agent.add_unit(unit1)
    agent.add_unit(unit2)

    additional_position = MapPosition(3, 3)
    agent.add_claimed_tile(additional_position)

    agent.kill()

    # Check state
    assert agent.state == AgentState.DONE
    assert len(agent.units) == 0
    assert len(agent._claimed_tiles) == 0
    assert agent.id in env.done_agents


def test_agent_get_observation(setup):
    env, city, agent_id, position_1, position_2 = setup
    agent = env.agents[agent_id]

    agent.money = 600
    agent.last_money_pl = 100
    agent.units = [MagicMock(strength=10), MagicMock(strength=20)]
    agent._claimed_tiles = {position_1, position_2}

    observation = agent.get_observation()
    assert observation[0] == 600
    assert math.isclose(observation[1], 0.02, rel_tol=1e-6, abs_tol=0.00001)
    assert observation[2] == 30


def test_agent_update_local_visibility(setup):
    env, city, agent_id, position_1, position_2 = setup
    agent = env.agents[agent_id]
    agent.visibility_range = 1

    agent.update_local_visibility(position_1)

    neighbours = env.map.get_surrounding_tiles(position_1, 1)
    for tile in neighbours:
        assert env.map.is_visible(tile.position, agent_id)


def test_agent_add_remove_unit(setup):
    env, city, agent_id, position_1, position_2 = setup
    agent = env.agents[agent_id]

    mock_unit1 = MagicMock()
    mock_unit1.owner.id = agent_id
    mock_unit2 = MagicMock()
    mock_unit2.owner.id = agent_id
    mock_unit3 = MagicMock()
    mock_unit3.owner.id = 1

    agent.add_unit(mock_unit1)
    agent.add_unit(mock_unit2)
    agent.add_unit(mock_unit3)  # Should not be added

    assert len(agent.units) == 2
    assert mock_unit1 in agent.units
    assert mock_unit2 in agent.units
    assert mock_unit3 not in agent.units

    agent.remove_unit(mock_unit1)
    assert len(agent.units) == 1
    assert mock_unit1 not in agent.units
    assert mock_unit2 in agent.units

    # Attempt to remove a unit not in the list
    agent.remove_unit(mock_unit3)  # Should do nothing
    assert len(agent.units) == 1


def test_agent_claimed_tiles(setup):
    env, city, agent_id, position_1, position_2 = setup
    agent = env.agents[agent_id]

    # Initially, only the starting position is claimed
    assert len(agent.get_claimed_tiles()) == 1

    new_position = MapPosition(4, 4)
    agent.add_claimed_tile(new_position)
    assert new_position in agent.get_claimed_tiles()


def test_agent_add_remove_city(setup):
    env, city, agent_id, position_1, position_2 = setup
    agent = env.agents[agent_id]

    assert len(agent.cities) == 1
    founding_city = agent.cities[0]

    # Add another city
    new_city = City(agent_id, MapPosition(5, 5), {})
    agent.add_city(new_city)
    assert len(agent.cities) == 2

    # Remove one city
    agent.remove_city(new_city)
    assert len(agent.cities) == 1

    # Remove random city, should not affect the agent
    agent.remove_city(new_city)
    assert len(agent.cities) == 1

    agent.remove_city(founding_city)
    assert len(agent.cities) == 0
    assert agent.state == AgentState.DONE
    assert agent.id in env.done_agents
