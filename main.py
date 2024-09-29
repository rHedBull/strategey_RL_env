from RL_env.environment import MapEnvironment

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
    # TODO check if hyperparameters are valid


def main():
    hyperparameters_path = './test_env/hyperparameters.json'
    env_settings_path = './test_env/env_settings.json'
    run_settings_path = './test_env/run_settings.json'

    hyperparameters = Settings(hyperparameters_path)
    env_settings = Settings(env_settings_path)
    run_settings = Settings(run_settings_path)

    #check_settings(hyperparameters, env_settings, run_settings)
    numb_agents = run_settings.get_setting('num_agents')
    screen = setup_screen(True, 1000)
    env = MapEnvironment(env_settings, numb_agents, True, screen, 'player')
    run = Run(run_settings, hyperparameters, env)
    run.run()

# clear TF logs
# run TF board
# tensorboard --logdir logs

if __name__ == "__main__":
    main()


# TODO Q table for agents
# TODO more complex map
# TODO add get actions for agents funciton to env
