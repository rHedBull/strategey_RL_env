import json

import gymnasium as gym
import numpy as np
import pytest

from strategyRLEnv.environment import MapEnvironment


@pytest.fixture
def env():
    # open settings file
    with open("test_env_settings.json", "r") as f:
        env_settings = json.load(f)

    env = MapEnvironment(env_settings, 2, "rgb_array")
    yield env
    env.close()


def test_reset(env):
    # Test reset function
    old_map = env.map.id

    observation, info = env.reset()
    new_map = env.map.id
    # compare uuids
    assert not old_map == new_map, "Reset should create a new map"

    map_observation = observation["map"]
    agent_observation = observation["agents"]

    assert isinstance(
        map_observation, np.ndarray
    ), "Reset should return an map_observation of type np.ndarray"

    assert isinstance(
        agent_observation, np.ndarray
    ), "Reset should return an map_observation of type np.ndarray"

    # call with invalid input should raise exception
    with pytest.raises(ValueError):
        env.reset(seed="invalid")


def test_step(env):
    # Test step function
    env.reset()
    action_space = env.action_space
    agent_0_random_actions = [action_space.sample()]
    agent_1_random_actions = [
        action_space.sample(),
        action_space.sample(),
    ]

    observation, reward, terminated, truncated, info = env.step(
        [agent_0_random_actions]
    )
    observation, reward, terminated, truncated, info = env.step(
        [agent_0_random_actions, agent_1_random_actions]
    )

    map_observation = observation["map"]
    agent_observation = observation["agents"]

    assert isinstance(
        map_observation, np.ndarray
    ), "Reset should return an map_observation of type np.ndarray"

    assert isinstance(
        agent_observation, np.ndarray
    ), "Reset should return an map_observation of type np.ndarray"
    assert isinstance(reward, np.ndarray), "Reward should be a numpy array"
    assert isinstance(terminated, list), "Terminated flag should be a boolean"
    assert isinstance(terminated[0], bool), "Terminated should be list of bools"
    assert isinstance(truncated, list), "Truncated flag should be a boolean"
    assert isinstance(truncated[0], bool), "truncated should be list of bools"
    assert isinstance(info, dict), "Info should be a dictionary"

    observation, reward, terminated, truncated, info = env.step(
        [agent_0_random_actions]
    )
    assert isinstance(
        map_observation, np.ndarray
    ), "Reset should return an map_observation of type np.ndarray"

    assert isinstance(
        agent_observation, np.ndarray
    ), "Reset should return an map_observation of type np.ndarray"
    assert isinstance(reward, np.ndarray), "Reward should be a numpy array"
    assert isinstance(terminated, list), "Terminated flag should be a boolean"
    assert isinstance(terminated[0], bool), "Terminated should be list of bools"
    assert isinstance(truncated, list), "Truncated flag should be a boolean"
    assert isinstance(truncated[0], bool), "truncated should be list of bools"
    assert isinstance(info, dict), "Info should be a dictionary"

    with pytest.raises(ValueError):
        actions = [[[0, 0]]]
        observation, reward, terminated, truncated, info = env.step(actions)

    with pytest.raises(ValueError):
        action_set = set()
        observation, reward, terminated, truncated, info = env.step(action_set)


def test_action_space(env):
    action_space = env.action_space
    assert isinstance(
        action_space, gym.spaces.Space
    ), "Action space should be an instance of gym.spaces.Space"

    # assumption on test_env_settings.json with map size 100x100
    assert action_space == gym.spaces.MultiDiscrete(
        [9, 100, 100]
    ), "Action space should be a MultiDiscrete space with 3 dimensions"

    random_action = action_space.sample()
    assert action_space.contains(
        random_action
    ), "Sampled action should be valid in the action space"


def test_observation_space(env):
    # Test observation space
    observation_space = env.observation_space
    assert isinstance(
        observation_space, gym.spaces.Space
    ), "Observation space should be an instance of gym.spaces.Space"
    observation, _ = env.reset()

    assert observation_space.contains(
        observation
    ), "Observation should be valid in the observation space"


def test_render(env):
    # Test render function in different modes
    with open("test_env_settings.json", "r") as f:
        env_settings = json.load(f)
    env_human = MapEnvironment(
        env_settings, 2, "human"
    )  # human mode causes trouble with numpy versions while testing
    env_human.reset()

    # Test render in 'human' mode (already specified when creating the environment)
    try:
        render_result_human = env_human.render()
        assert isinstance(
            render_result_human, (type(None), np.ndarray)
        ), "Render in 'human' mode should return None or an image (np.ndarray)"
        if isinstance(render_result_human, np.ndarray):
            assert (
                render_result_human.ndim == 3 and render_result_human.shape[2] == 3
            ), "Render in 'human' mode should return an RGB image if not None"
    except Exception as e:
        pytest.fail(f"Render in 'human' mode raised an exception: {e}")

    env.reset()
    render_result_rgb = env.render()
    assert isinstance(
        render_result_rgb, np.ndarray
    ), "Render in 'rgb_array' mode should return an image (np.ndarray)"
    assert (
        render_result_rgb.ndim == 3 and render_result_rgb.shape[2] == 3
    ), "Render in 'rgb_array' mode should return an RGB image"
    env_human.close()
    env.close()


def test_close(env):
    env.close()
    assert True, "Environment should close without errors"


def test_seed(env):
    # Test seed function
    env.reset(seed=42)
    assert True, "Seeding should not raise any errors"
