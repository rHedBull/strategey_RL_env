import pytest
import numpy as np
import gymnasium as gym

from rl_env.environment import MapEnvironment


@pytest.fixture
def env():
    env = MapEnvironment("test_env_settings.json", 2, "rgb_array")
    yield env
    env.close()

def test_reset(env):
    # Test reset function
    observation, agent_observation, visibility_masks, info = env.reset()
    assert isinstance(observation, np.ndarray), "Reset should return an observation of type np.ndarray"
    assert isinstance(agent_observation, np.ndarray), "Reset should return an agent observation of type np.ndarray"
    assert isinstance(visibility_masks, np.ndarray), "Reset should return visibility masks of type np.ndarray"
    assert isinstance(info, dict), "Reset should return info as a dictionary"

def test_step(env):
    # Test step function
    env.reset()
    action_space = env.action_space
    random_action = action_space.sample()
    observation, reward, terminated, truncated, info = env.step(random_action)

    assert isinstance(observation, np.ndarray), "Step should return an observation of type np.ndarray"
    assert isinstance(reward, (float, int)), "Reward should be a float or an int"
    assert isinstance(terminated, bool), "Terminated flag should be a boolean"
    assert isinstance(truncated, bool), "Truncated flag should be a boolean"
    assert isinstance(info, dict), "Info should be a dictionary"

def test_action_space(env):

    action_space = env.action_space
    assert isinstance(action_space, gym.spaces.Space), "Action space should be an instance of gym.spaces.Space"
    random_action = action_space.sample()
    assert action_space.contains(random_action), "Sampled action should be valid in the action space"

def test_observation_space(env):
    # Test observation space
    observation_space = env.observation_space
    assert isinstance(observation_space, gym.spaces.Space), "Observation space should be an instance of gym.spaces.Space"
    observation, _ = env.reset()
    assert observation_space.contains(observation), "Observation should be valid in the observation space"

def test_render(env):
    # Test render function in different modes
    env_human = MapEnvironment("test_env_settings.json", 2, "human")
    env_human.reset()

    # Test render in 'human' mode (already specified when creating the environment)
    try:
        render_result_human = env_human.render()
        assert isinstance(render_result_human, (
        type(None), np.ndarray)), "Render in 'human' mode should return None or an image (np.ndarray)"
        if isinstance(render_result_human, np.ndarray):
            assert render_result_human.ndim == 3 and render_result_human.shape[
                2] == 3, "Render in 'human' mode should return an RGB image if not None"
    except Exception as e:
        pytest.fail(f"Render in 'human' mode raised an exception: {e}")

    env.reset()
    render_result_rgb = env.render()
    assert isinstance(render_result_rgb, np.ndarray), "Render in 'rgb_array' mode should return an image (np.ndarray)"
    assert render_result_rgb.ndim == 3 and render_result_rgb.shape[2] == 3, "Render in 'rgb_array' mode should return an RGB image"
    env.close()

def test_close(env):

    env.close()
    assert True, "Environment should close without errors"

def test_seed(env):
    # Test seed function
    env.reset(seed=42)
    assert True, "Seeding should not raise any errors"
