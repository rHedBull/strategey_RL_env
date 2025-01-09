from enum import Enum

COLOR_DEFAULT_LAND = (34, 139, 34)
COLOR_DEFAULT_RIVER = (0, 255, 255)
COLOR_DEFAULT_OCEAN = (76, 49, 252)
COLOR_DEFAULT_MARSH = (27, 96, 0)
COLOR_DEFAULT_MOUNTAIN = (
    80,
    10,
    10,
)
COLOR_DEFAULT_DESERT = (249, 233, 76)

# agent interaction colors
COLOR_DEFAULT_BORDER = (255, 255, 255)
PLAYER_COLOR = (0, 0, 255)

# agent color red, blue, orange, yellow, purple,
AGENT_COLORS = [
    (0, 0, 255),
    (255, 0, 0),
    (255, 165, 0),
    (255, 255, 0),
    (128, 0, 128),
    (0, 255, 0),
]

road_color = (128, 128, 128)
bridge_color = (139, 69, 19)

OWNER_DEFAULT_TILE = -1


class LandType(Enum):
    LAND = 0
    OCEAN = 1
    RIVER = 2
    MARSH = 3
    MOUNTAIN = 4
    DESERT = 5  # if you change this you need to change observation space


class ResourceType(Enum):
    GRAIN = 2
    METAL = 1
    NONE = 0


class BuildingType(Enum):
    CITY = "build_city"
    ROAD = "build_road"
    BRIDGE = "build_bridge"
    FARM = "build_farm"
    MINE = "build_mine"


def land_type_color(land_type: LandType):
    if land_type == LandType.LAND:
        return COLOR_DEFAULT_LAND
    elif land_type == LandType.OCEAN:
        return COLOR_DEFAULT_OCEAN
    elif land_type == LandType.RIVER:
        return COLOR_DEFAULT_RIVER
    elif land_type == LandType.MARSH:
        return COLOR_DEFAULT_MARSH
    elif land_type == LandType.MOUNTAIN:
        return COLOR_DEFAULT_MOUNTAIN
    elif land_type == LandType.DESERT:
        return COLOR_DEFAULT_DESERT
    else:
        return COLOR_DEFAULT_LAND


BUILDING_IDS = {
    BuildingType.CITY: 0,
    BuildingType.ROAD: 1,
    BuildingType.BRIDGE: 2,
    BuildingType.FARM: 3,
    BuildingType.MINE: 4,
}

ALLOWED_BUILDING_PLACEMENTS = {
    BuildingType.CITY: {
        LandType.LAND,
        LandType.DESERT,
        LandType.MARSH,
    },
    BuildingType.ROAD: {
        LandType.LAND,
        LandType.DESERT,
        LandType.MARSH,
        LandType.MOUNTAIN,
    },
    BuildingType.BRIDGE: {LandType.RIVER, LandType.OCEAN},
    BuildingType.FARM: {LandType.LAND, LandType.MARSH},
    BuildingType.MINE: {LandType.MOUNTAIN},
    "UNIT": {LandType.LAND, LandType.MARSH, LandType.DESERT}
    # Add mappings for other building types
}

max_agent_id = 63  # based on current setup of visibility map, would have to use other datatype or multiple maps for more agents

ADJACENCY_MULTIPLIERS = {
    BuildingType.MINE: {
        BuildingType.ROAD: {"radius": 1, "multiplier": 3.33},
        BuildingType.BRIDGE: {"radius": 1, "multiplier": 2.0},
    },
    BuildingType.FARM: {
        BuildingType.ROAD: {"radius": 1, "multiplier": 2.0},
        BuildingType.BRIDGE: {"radius": 1, "multiplier": 2.0},
    },
    # Add other building types and their adjacency rules as needed
}

farm_mine_health = 50
city_health = 100
healing_base = 10