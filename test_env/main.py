from RL_env.MapEnvironment import MapEnvironment

import pygame

from RL_env.Settings import Settings
from test_env.Run import Run


def setup_screen(rendering, screen_size):
    if rendering:
        screen = pygame.display.set_mode((screen_size, screen_size))
        pygame.display.set_caption('Agent-based Landmass Generation')
        screen.fill((0, 0, 0))
        return screen


def check_settings(hyperparameters, env_settings, run_settings):
    if run_settings.get_setting('num_agents') != env_settings.get_setting('num_agents'):
        raise ValueError("Number of agents in run settings and environment settings do not match")
    if env_settings.get_setting('tiles') < env_settings.get_setting('map_agents') * \
            env_settings.get_setting('map_agents_water'):
        raise ValueError('Map size is too small for number of agents')


def main():
    hyperparameters_path = './test_env/hyperparameters.json'
    env_settings_path = './test_env/env_settings.json'
    run_settings_path = './test_env/run_settings.json'
    hyperparameters = Settings(hyperparameters_path)
    env_settings = Settings(env_settings_path)
    run_settings = Settings(run_settings_path)

    check_settings(hyperparameters, env_settings, run_settings)
    screen = setup_screen(True, 1000)
    env = MapEnvironment(env_settings, 4, True, screen)
    run = Run(run_settings, hyperparameters, env)
    run.run()


if __name__ == "__main__":
    main()

# TODO make player always same color if rendering with player
# TODO proper rewared storing
# TODO proper stats tracking
# TODO stats visualization after one game
# TODO stats visualization after multiple games
# TODO stats tracking, visualization during game( player)

# TODO Q table for agents
# TODO more complex map
# TODO add get actions for agents funciton to env

# Todo simplify code
# TODO clearly define hyperparameters and agents, map settings
# TODO uuid based on agent and map settings, for storing
