# land specific colors
COLOR_DEFAULT_LAND = (34, 139, 34)
COLOR_DEFAULT_WATER = (0, 255, 255)

# agent interaction colors
COLOR_DEFAULT_BORDER = (255, 255, 255)
PLAYER_COLOR = (0, 0, 255)

# agent color red, blue, orange, yellow, purple,
AGENT_COLORS = [(0, 0, 255), (255, 0, 0), (255, 165, 0), (255, 255, 0), (128, 0, 128), (0, 255, 0)]


VALUE_DEFAULT_LAND = 0
VALUE_DEFAULT_WATER = 1
LAND = [['land', 10, COLOR_DEFAULT_LAND], ['water', 1, COLOR_DEFAULT_WATER]]
# TODO extend this to more land types
# TODO make this more customizable
# [ [land_type_name, land_base_value, land_color], ...]

OWNER_DEFAULT_TILE = -1