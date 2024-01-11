import uuid

from RL_env.MapEnvironment import MapEnvironment
from RL_env.Settings import Settings
from test_env.Player import Player
from test_env.Agent import Agent

import pygame

from test_env.Run import Run


def setup_screen(rendering, screen_size):
    if rendering:
        screen = pygame.display.set_mode((screen_size, screen_size))
        pygame.display.set_caption('Agent-based Landmass Generation')
        screen.fill((0, 0, 0))
        return screen

def main():
    screen = setup_screen(True, 1000)
    env = MapEnvironment("./test_env/env_settings.json", 10, True, screen)
    run = Run("./test_env/run_settings.json", "./test_env/hyperparameters.json", env)
    run.check_settings()
    run.run()


def store_stats(settings_file, agents, map, step):
    pass


if __name__ == "__main__":
    main()

# TODO proper rewared storing
# TODO proper stats tracking
# TODO stats visualization after one game
# TODO stats visualization after multiple games
# TODO stats tracking, visualization during game( player)

# TODO Q table for agents
# TODO more complex map

# Todo simplify code
# TODO clearly define hyperparameters and agents, map settings
# TODO uuid based on agent and map settings, for storing
