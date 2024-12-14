import math
import os
import pickle
import uuid
import random

import numpy as np

from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.map.map_agent import Map_Agent
from strategyRLEnv.map.map_settings import LandType
from strategyRLEnv.map.map_square import Map_Square
from strategyRLEnv.map.sim_map import Map

def topology_to_map(topology_array):
    # Convert the topology array to a map

    created_map = Map()
    created_map.width = len(topology_array[0])
    created_map.height = len(topology_array)
    created_map.tiles = created_map.height * created_map.width

    squares = [[None for _ in range(created_map.height)] for _ in range(created_map.width)]

    # Create map squares
    for x_index in range(created_map.width):
        for y_index in range(created_map.height):
            square = Map_Square(y_index * created_map.width + x_index, MapPosition(x_index, y_index))
            square.set_land_type(LandType(topology_array[y_index][x_index]))
            squares[x_index][y_index] = square

    created_map.squares = squares
    created_map.reset()

    return created_map

def generate_finished_map(connected_env, map_settings):
    width = map_settings.get("map_width", 100)
    height = map_settings.get("map_height", 100)

    water_percentage = map_settings.get("water_budget_per_agent", 0.3)
    mountain_percentage = map_settings.get("mountain_budget_per_agent", 0.1)
    dessert_percentage = map_settings.get("dessert_budget_per_agent", 0.1)

    topology_array = create_topologies(1, width, height, water_percentage, mountain_percentage, dessert_percentage)
    finished_map = topology_to_map(topology_array[0])

    finished_map.env = connected_env

    if height > width:
        finished_map.tile_size = int(connected_env.screen.get_height() / height)
    else:
        finished_map.tile_size = int(connected_env.screen.get_width() / width)
    finished_map.tile_size = max(1, finished_map.tile_size)

    return finished_map

def generate_map_topologies(numb, map_settings, path=None):
    # Ensure output directory exists
    os.makedirs(path, exist_ok=True)
    print("Generating {} maps. Output directory: {}".format(numb, path))

    width = map_settings.get("map_width", 100)
    height = map_settings.get("map_height", 100)

    water_percentage = map_settings.get("water_budget_per_agent", 0.3)
    mountain_percentage = map_settings.get("mountain_budget_per_agent", 0.1)
    dessert_percentage = map_settings.get("dessert_budget_per_agent", 0.1)

    # Generate maps using settings and save to file
    map_arrays = create_topologies(numb, width, height, water_percentage, mountain_percentage, dessert_percentage)
    for i in range(numb):
        map_array = map_arrays[i]
        map_name = generate_map_name(width, height, water_percentage, mountain_percentage, dessert_percentage, i)
        map_file_path = os.path.join(path, f"{map_name}.pickle")
        try:
            with open(map_file_path, "wb") as file:
                pickle.dump(map_array, file)
        except IOError as e:
            print(f"Failed to save map to {map_file_path}: {e}")
    print(f"{numb} maps generated and saved to {path}")

def let_map_agent_run(map_array, land_type_percentage, tiles, LAND_TYPE_VALUE):
    if land_type_percentage < 0:
        return

    map_copy = map_array.copy()
    total_tile_budget = tiles * land_type_percentage
    numb_agents = int(min(10, (tiles * 0.01) + 1))
    tile_budget_per_agent = int((total_tile_budget / numb_agents))

    if (numb_agents * tile_budget_per_agent) > 0:
        agents = [
            Map_Agent(
                random.randint(0, int(math.sqrt(tiles) - 1)),
                random.randint(0, int(math.sqrt(tiles) - 1)),
                tile_budget_per_agent,
            )
            for i in range(numb_agents)
        ]

        running = True
        while running:
            for agent in agents:
                agent.random_walk(map_copy, tiles, LAND_TYPE_VALUE)
                if agent.tile_budget == 0:
                    agents.remove(agent)
                if len(agents) == 0:
                    running = False
    return map_copy

def create_topologies(num, width, height, water_percentage, mountain_percentage, dessert_percentage):
    # Initialize the 2D list with the appropriate dimensions
    map_arrays = []
    for i in range(num):
        map_array = np.zeros((width, height), dtype=np.int64)
        total_tiles = width * height

        # mountain agents
        map_array = let_map_agent_run(map_array, mountain_percentage, total_tiles, LandType.MOUNTAIN)

        # dessert agents
        map_array = let_map_agent_run(map_array, dessert_percentage, total_tiles, LandType.DESERT)

        # water agents
        map_array = let_map_agent_run(map_array, water_percentage, total_tiles, LandType.OCEAN)
        map_arrays.append(map_array)


    # post processing is done together
    for m in range(num):
        for row in range(height):
            for col in range(width):
                map_arr = map_arrays[m]
                tile = map_arr[row][col]
                # check if water around
                if tile != LandType.OCEAN.value:
                    if is_adjacent_to_ocean(row, col, width, height, map_arr):
                        map_arr[row][col] = LandType.MARSH.value

    return map_arrays

def is_adjacent_to_ocean(x, y, width, height, array):
    """
    Helper function to check if a square at position (x, y) is adjacent to an ocean.
    """
    # Check left neighbor
    if x > 0 and array[x - 1][y] == LandType.OCEAN.value:
        return True
    # Check right neighbor
    if x < width - 1 and array[x + 1][y]== LandType.OCEAN.value:
        return True
    # Check top neighbor
    if y > 0 and array[x][y - 1] == LandType.OCEAN.value:
        return True
    # Check bottom neighbor
    if y < height - 1 and array[x][y + 1] == LandType.OCEAN.value:
        return True
    return False

def generate_map_name(width, height, water_percentage, mountain_percentage, dessert_percentage, resource_density):
    settings_values = (
        f"{width}_{height}_{water_percentage}_{mountain_percentage}_{dessert_percentage}_{resource_density}"
    )
    unique_id = uuid.uuid4()
    map_name = f"map_{settings_values}_{unique_id}"
    return map_name

def load_topography_to_Map(file_path):
    """Load the map topography and resources from a pickle file."""

    with open(file_path, "rb") as file:
        map_array = pickle.load(file)

    # Reconstruct the map object
    height = len(map_array)
    width = len(map_array[0])
    tiles = height * width
    created_map = topology_to_map(map_array)
    return created_map

if __name__ == "__main__":
    # Generate maps
    map_settings = {
        "map_width": 100,
        "map_height": 100,
        "water_budget_per_agent": 0.3,
        "mountain_budget_per_agent": 0.1,
        "dessert_budget_per_agent": 0.1,
    }
    generate_map_topologies(1, map_settings, path="maps")
    print("Maps generated")
    # Load maps
    map_file_path = "maps/map_100_100_0.3_0.1_0.1_0_d06f76f5-20ac-4bfc-94ca-dbfeed365503.pickle"
    loaded_map = load_topography_to_Map(map_file_path)
    print("Map loaded")