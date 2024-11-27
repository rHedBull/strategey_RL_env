import argparse
import logging

import pygame
from settings.settings import Settings

from rl_env.environment import MapEnvironment
from test_env.Run import Run

# Set up logging configuration to display info messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_screen(rendering: bool, screen_size: int):
    # Set up the rendering screen if rendering is enabled
    if rendering:
        screen = pygame.display.set_mode((screen_size, screen_size))
        pygame.display.set_caption("Agent-based Landmass Generation")
        screen.fill((0, 0, 0))  # Fill the screen with black color
        return screen
    return None


def check_settings(hyperparameters, env_settings, run_settings):
    if run_settings.get_setting("num_agents") != env_settings.get_setting("num_agents"):
        raise ValueError(
            "Number of agents in run settings and environment settings do not match"
        )
    if env_settings.get_setting("tiles") < env_settings.get_setting(
        "map_agents"
    ) * env_settings.get_setting("map_agents_water"):
        raise ValueError("Map size is too small for number of agents")
    # TODO check if hyperparameters are valid


def main(args):
    hyperparameters_path = args.hyperparameters_path
    env_settings_path = args.env_settings_path
    run_settings_path = args.run_settings_path
    map_file = args.map_file

    hyperparameters = Settings(hyperparameters_path)
    env_settings = Settings(env_settings_path)
    run_settings = Settings(run_settings_path)
    rendering = args.rendering
    game_type = args.game_type
    logging = args.logging

    numb_agents = run_settings.get_setting("num_agents")
    # check_settings(hyperparameters, env_settings, run_settings)

    # Set up the environment and run the training
    screen = setup_screen(
        args.rendering, args.screen_size
    )  # Set up the rendering screen if required
    env = MapEnvironment(
        env_settings,
        numb_agents,
        screen,
        render_mode=rendering,
        game_type=game_type,
        map_file=map_file,
    )  # Initialize the environment
    run = Run(
        run_settings, hyperparameters, env
    )  # Initialize the Run class with settings and environment
    run.run()


if __name__ == "__main__":
    # Set up argument parsing for command-line arguments
    parser = argparse.ArgumentParser(description="Run the RL agent training.")
    parser.add_argument(
        "--hyperparameters_path",
        type=str,
        default="./test_env/hyperparameters.json",
        help="Path to the hyperparameters JSON file",
    )
    parser.add_argument(
        "--env_settings_path",
        type=str,
        default="./test_env/env_settings.json",
        help="Path to the environment settings JSON file",
    )
    parser.add_argument(
        "--run_settings_path",
        type=str,
        default="./test_env/run_settings.json",
        help="Path to the run settings JSON file",
    )
    parser.add_argument(
        "--screen_size", type=int, default=1000, help="Screen size for rendering"
    )
    parser.add_argument(
        "--rendering",
        type=str,
        default="human",
        help="Flag to enable or disable rendering",
    )
    parser.add_argument(
        "--game_type",
        type=str,
        default="human",
        help="Flag to enable or human player",
    )
    parser.add_argument(
        "--map_file",
        type=str,
        default=None,
        help="Path to the pre generated map file",
    )
    parser.add_argument(
        "--logging", type=bool, default=True, help="Flag to enable or disable logging"
    )
    args = parser.parse_args()

    # Call the main function with parsed arguments
    main(args)
