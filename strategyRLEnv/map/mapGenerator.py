import math
import os
import pickle
import random
import uuid

import numpy as np

from strategyRLEnv.map.Map import Map
from strategyRLEnv.map.map_settings import LandType, ResourceType
from strategyRLEnv.map.MapAgent import Map_Agent
from strategyRLEnv.map.MapPosition import MapPosition
from strategyRLEnv.map.MapSquare import Map_Square


def topology_to_map(topology_array):
    # Convert the topology array to a map

    created_map = Map(topology_array)
    created_map.width = len(topology_array[0])
    created_map.height = len(topology_array)
    created_map.tiles = created_map.height * created_map.width

    squares = [
        [None for _ in range(created_map.height)] for _ in range(created_map.width)
    ]

    # Create map squares
    for x_index in range(created_map.width):
        for y_index in range(created_map.height):
            square = Map_Square(
                y_index * created_map.width + x_index, MapPosition(x_index, y_index)
            )
            square.set_land_type(LandType(topology_array[y_index][x_index][0]))
            square.add_resource(ResourceType(topology_array[y_index][x_index][1]))
            squares[x_index][y_index] = square

    created_map.squares = squares
    created_map.reset()

    return created_map


def generate_finished_map(connected_env, map_settings=None, path_to_map_file=None):
    if path_to_map_file:
        with open(path_to_map_file, "rb") as file:
            map_array = pickle.load(file)
        height = len(map_array)
        width = len(map_array[0])
        finished_map = topology_to_map(map_array)
    else:
        if not map_settings:
            raise ValueError("No map settings or path to map file provided")
        width = map_settings.get("map_width", 100)
        height = map_settings.get("map_height", 100)

        water_percentage = map_settings.get("water_budget_per_agent", 0.3)
        mountain_percentage = map_settings.get("mountain_budget_per_agent", 0.1)
        dessert_percentage = map_settings.get("dessert_budget_per_agent", 0.1)
        resource_density = map_settings.get("resource_density", 0.05)

        topology_array = create_topologies(
            1,
            width,
            height,
            water_percentage,
            mountain_percentage,
            dessert_percentage,
            resource_density,
        )
        finished_map = topology_to_map(topology_array[0])

    finished_map.env = connected_env

    if height > width:
        finished_map.tile_size = int(connected_env.screen.get_height() / height)
    else:
        finished_map.tile_size = int(connected_env.screen.get_width() / width)
    finished_map.tile_size = max(1, finished_map.tile_size)

    return finished_map


def generate_map_topologies(numb, map_settings, seed=None, path=None):
    """
    Generate map topologies and save them to files.
    Args:
        numb: number of maps to generate
        map_settings: dictionary with settings for the map generation
        seed: seed for random number generation
        path: path to save the maps to

    Returns:

    """

    if seed:
        raise NotImplementedError("Seed is not implemented yet")

    # Ensure output directory exists
    os.makedirs(path, exist_ok=True)
    print("Generating {} maps. Output directory: {}".format(numb, path))

    width = map_settings.get("map_width", 100)
    height = map_settings.get("map_height", 100)

    water_percentage = map_settings.get("water_budget_per_agent", 0.3)
    mountain_percentage = map_settings.get("mountain_budget_per_agent", 0.1)
    dessert_percentage = map_settings.get("dessert_budget_per_agent", 0.1)
    resource_density = map_settings.get("resource_density", 0.05)

    # Generate maps using settings and save to file
    map_arrays = create_topologies(
        numb,
        width,
        height,
        water_percentage,
        mountain_percentage,
        dessert_percentage,
        resource_density,
    )

    for i in range(numb):
        map_array = map_arrays[i]
        map_name = generate_map_name(
            width, height, water_percentage, mountain_percentage, dessert_percentage, i
        )
        map_file_path = os.path.join(path, f"{map_name}.pickle")
        try:
            with open(map_file_path, "wb") as file:
                pickle.dump(map_array, file)
        except IOError as e:
            print(f"Failed to save map to {map_file_path}: {e}")
    print(f"{numb} maps generated and saved to {path}")


def let_map_agent_run(
    map_arrays, land_type_percentage, tiles, LAND_TYPE_VALUE, position
):
    if land_type_percentage < 0:
        return

    map_copy = [m.copy() for m in map_arrays]

    total_tile_budget = tiles * land_type_percentage
    numb_agents_per_map = int(min(10, (tiles * 0.01) + 1))
    tile_budget_per_agent = int((total_tile_budget / numb_agents_per_map))
    map_count = len(map_arrays)

    if (numb_agents_per_map * tile_budget_per_agent) <= 0:
        return map_copy

    for m in range(map_count):
        agents = []
        for i in range(numb_agents_per_map):
            agents.append(
                Map_Agent(
                    position.x,
                    position.y,
                    m,
                    tile_budget_per_agent,
                )
            )

        while agents:
            left_agents = len(agents)
            # Generate random walks on GPU
            walks = np.random.randint(0, 8, size=left_agents)

            # We iterate over a snapshot copy of agents
            # so we can safely remove them from the original list
            for i, agent in enumerate(list(agents)):
                walk = walks[i].item()  # single integer
                agent.step(map_copy, tiles, walk, LAND_TYPE_VALUE)
                if agent.tile_budget <= 0:
                    agents.remove(agent)

    return map_copy


def create_topologies(
    num,
    width,
    height,
    water_percentage,
    mountain_percentage,
    dessert_percentage,
    resource_density=0.05,
):
    # Initialize the 2D list with the appropriate dimensions

    topology_arrays = [np.zeros((width, height, 1), dtype=np.int64) for _ in range(num)]
    resource_arr = [np.zeros((width, height, 1), dtype=np.int64) for _ in range(num)]
    total_tiles = width * height

    # use numpy to generate 6 random ints between 0 and 100
    random_values = np.random.randint(0, width, 6)

    # mountain agents
    topology_arrays = let_map_agent_run(
        topology_arrays,
        mountain_percentage,
        total_tiles,
        LandType.MOUNTAIN,
        MapPosition(random_values[0], random_values[1]),
    )

    # dessert agents
    topology_arrays = let_map_agent_run(
        topology_arrays,
        dessert_percentage,
        total_tiles,
        LandType.DESERT,
        MapPosition(random_values[2], random_values[3]),
    )

    # water agents
    topology_arrays = let_map_agent_run(
        topology_arrays,
        water_percentage,
        total_tiles,
        LandType.OCEAN,
        MapPosition(random_values[4], random_values[5]),
    )

    # expand topology arrays unsqueeze
    map_arrays = np.concatenate((topology_arrays, resource_arr), axis=3)

    # post processing is done together
    for m in range(num):
        for row in range(height):
            for col in range(width):
                map_arr = map_arrays[m]
                tile = map_arr[row][col]
                land = tile[0]
                # check if water around
                if land != LandType.OCEAN.value:
                    if is_adjacent_to_ocean(row, col, width, height, map_arr):
                        map_arr[row][col][0] = LandType.MARSH.value

                if land == LandType.LAND.value:
                    if random.random() < resource_density:
                        map_arr[row][col][1] = ResourceType.GRAIN.value

                if land == LandType.MOUNTAIN.value:
                    if random.random() < resource_density:
                        map_arr[row][col][1] = ResourceType.METAL.value

    return map_arrays


def is_adjacent_to_ocean(x, y, width, height, array):
    """
    Helper function to check if a square at position (x, y) is adjacent to an ocean.
    """
    # Check left neighbor
    if x > 0 and array[x - 1][y][0] == LandType.OCEAN.value:
        return True
    # Check right neighbor
    if x < width - 1 and array[x + 1][y][0] == LandType.OCEAN.value:
        return True
    # Check top neighbor
    if y > 0 and array[x][y - 1][0] == LandType.OCEAN.value:
        return True
    # Check bottom neighbor
    if y < height - 1 and array[x][y + 1][0] == LandType.OCEAN.value:
        return True
    return False


def generate_map_name(
    width,
    height,
    water_percentage,
    mountain_percentage,
    dessert_percentage,
    resource_density,
):
    settings_values = f"{width}_{height}_{water_percentage}_{mountain_percentage}_{dessert_percentage}_{resource_density}"
    unique_id = uuid.uuid4()
    map_name = f"map_{settings_values}_{unique_id}"
    return map_name


def generate_maps(num_maps: int, map_settings=None, seed=None, out_dir=None):
    """
    Generates a set of maps for the environment to use.
    Args:
        num_maps (int): The number of maps to generate.
    """
    maps = generate_map_topologies(num_maps, map_settings, seed, out_dir)

    return maps
