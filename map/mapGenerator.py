import logging
import os
import uuid

from settings.settings import Settings

from map.sim_map import Map

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


def generate_map_name(settings):
    # Use settings values and a UUID to generate a unique map name
    settings_values = (
        f"width_{settings.get_setting('map_width')}"
        f"_tiles_{settings.get_setting('tiles')}"
        f"_water_{settings.get_setting('water_budget_per_agent')}"
        f"_mountain_{settings.get_setting('mountain_budget_per_agent')}"
        f"_dessert_{settings.get_setting('dessert_budget_per_agent')}"
        f"_resource_{settings.get_setting('resource_density')}"
    )
    unique_id = uuid.uuid4()

    map_name = f"map_{settings_values}_{unique_id}"
    logging.debug(f"Generated map name: {map_name}")
    return map_name


def generate_maps(n, settings, path):
    # Ensure output directory exists
    os.makedirs(path, exist_ok=True)
    logging.info(f"Output directory ensured at: {path}")
    env_settings = Settings(settings)
    for i in range(n):
        logging.info(f"Generating map {i + 1} of {n}")

        map_instance = Map()
        map_instance.create_map(env_settings)
        logging.debug(f"Map instance created with settings: {settings}")

        # Generate map name using settings and save to file
        map_name = generate_map_name(env_settings)
        map_file_path = os.path.join(path, f"{map_name}.pickle")

        try:
            map_instance.save_topography_resources(map_file_path)
            logging.info(f"Map saved successfully to: {map_file_path}")
        except IOError as e:
            logging.error(f"Failed to save map to {map_file_path}: {e}")


if __name__ == "__main__":
    # Load settings from file
    settings_path = "./env_settings.json"

    n = 2
    path = "../generatedMaps"
    logging.info(f"Starting map generation: {n} maps to be generated")
    generate_maps(n, settings_path, path)
    logging.info("Map generation completed")
