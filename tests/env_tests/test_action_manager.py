import json

import numpy as np
import pytest

from strategyRLEnv.ActionManager import create_action
from strategyRLEnv.actions.BuildCityAction import BuildCityAction
from strategyRLEnv.actions.BuildFarmAction import BuildFarmAction
from strategyRLEnv.actions.BuildRoadAction import (BuildBridgeAction,
                                                   BuildRoadAction)
from strategyRLEnv.actions.ClaimAction import ClaimAction
from strategyRLEnv.environment import MapEnvironment


class MockAgent:
    def __init__(self, id=0):
        self.id = id


@pytest.fixture
def env():
    # open settings file
    with open("test_env_settings.json", "r") as f:
        env_settings = json.load(f)

    env = MapEnvironment(env_settings, 2, "rgb_array")
    yield env
    env.close()


def test_create_action(env):
    agent_1 = MockAgent()

    action_type = "build_city"
    pos = (1, 1)

    build_city_action = create_action(agent_1, action_type, pos)
    assert isinstance(build_city_action, BuildCityAction)
    assert build_city_action.agent == agent_1
    assert build_city_action.position == pos

    # Test claim action creation
    action_type = "claim"
    claim_action = create_action(agent_1, action_type, pos)
    assert isinstance(claim_action, ClaimAction)
    assert claim_action.agent == agent_1
    assert claim_action.position == pos

    # Test build road action creation
    action_type = "build_road"
    build_road_action = create_action(agent_1, action_type, pos)
    assert isinstance(build_road_action, BuildRoadAction)
    assert build_road_action.agent == agent_1
    assert build_road_action.position == pos

    # Test build bridge action creation
    action_type = "build_bridge"
    build_bridge_action = create_action(agent_1, action_type, pos)
    assert isinstance(build_bridge_action, BuildBridgeAction)
    assert build_bridge_action.agent == agent_1
    assert build_bridge_action.position == pos

    # Test build farm action creation
    action_type = "build_farm"
    build_farm_action = create_action(agent_1, action_type, pos)
    assert isinstance(build_farm_action, BuildFarmAction)
    assert build_farm_action.agent == agent_1
    assert build_farm_action.position == pos

    # Test unknown action type
    action_type = "unknown"
    unknown_action = create_action(agent_1, action_type, pos)
    assert unknown_action is None


def test_apply_actions_no_conflicts(env):
    action_space = env.action_space
    agent_0_random_actions = [action_space.sample()]
    agent_1_random_actions = [
        action_space.sample(),
        action_space.sample(),
    ]  # test multiple actions per agent
    agent_2_random_actions = []  # test empty action
    agent_invalid_action = [[-1, 0, 0]]  # invalid action id

    reward, dones = env.action_manager.apply_actions(
        [agent_0_random_actions, agent_1_random_actions]
    )
    assert isinstance(reward, np.ndarray), "Reward should be a numpy array"
    assert isinstance(dones, np.ndarray), "Terminated flag should be an array of bools"

    reward, dones = env.action_manager.apply_actions(
        [agent_0_random_actions, agent_1_random_actions]
    )
    assert isinstance(reward, np.ndarray), "Reward should be a numpy array"
    assert isinstance(dones, np.ndarray), "Terminated flag should be an array of bools"

    reward, dones = env.action_manager.apply_actions([agent_2_random_actions])
    assert isinstance(reward, np.ndarray), "Reward should be a numpy array"
    assert isinstance(dones, np.ndarray), "Terminated flag should be an array of bools"

    with pytest.raises(ValueError):
        reward, dones = env.action_manager.apply_actions([agent_invalid_action])


def test_apply_actions_with_conflict(env):
    build_1 = [1, 1, 1]  # build on same position
    build_3 = [1, 2, 2]  # build same on different position
    conflicting_actions = [
        [build_1],
        [build_1],
        [build_3],
    ]  # same agent trying to build on same position
    conflicting_actions2 = [
        [build_1, build_3],
        [build_1],
    ]  # different agents trying to build on same position

    rewards, dones = env.action_manager.apply_actions(conflicting_actions)
    assert isinstance(rewards, np.ndarray), "Reward should be a numpy array"
    assert isinstance(dones, np.ndarray), "Terminated flag should be an array of bools"

    rewards, dones = env.action_manager.apply_actions(conflicting_actions2)
    assert isinstance(rewards, np.ndarray), "Reward should be a numpy array"
    assert isinstance(dones, np.ndarray), "Terminated flag should be an array of bools"

    # maybe test that one of the rewards is 0 and the other is  > 0


def test_resolve_conflict(env):
    agent_1 = MockAgent(id=1)
    agent_2 = MockAgent(id=2)

    build_city_1 = BuildCityAction(agent_1, (1, 1))
    build_city1_2 = BuildCityAction(agent_1, (1, 1))
    build_city_2 = BuildCityAction(agent_2, (2, 2))
    build_city_2_1 = BuildCityAction(agent_2, (1, 1))

    no_conflicts_map = {}
    no_conflicts_map.setdefault((1, 1), []).append(build_city_1)
    no_conflicts_map.setdefault((2, 2), []).append(build_city_2)

    conflict_map_1 = {}
    conflict_map_1.setdefault((1, 1), []).append(build_city_1)
    conflict_map_1.setdefault((1, 1), []).append(build_city1_2)

    conflict_map_2 = {}
    conflict_map_2.setdefault((1, 1), []).append(build_city_1)
    conflict_map_2.setdefault((1, 1), []).append(build_city_2_1)

    env.action_manager.conflict_map = no_conflicts_map
    out_proposed_actions = env.action_manager.resolve_conflict()
    assert len(out_proposed_actions) == 2

    env.action_manager.conflict_map = conflict_map_1
    out_proposed_actions = env.action_manager.resolve_conflict()
    assert len(out_proposed_actions) == 1
    # assert that conflicts resolved

    env.action_manager.conflict_map = conflict_map_2
    env.action_manager.resolve_conflict()
    assert len(out_proposed_actions) == 1
    # assert that conflicts resolved
