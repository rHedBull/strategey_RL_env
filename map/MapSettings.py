# land specific colors
COLOR_DEFAULT_LAND = (34, 139, 34)
COLOR_DEFAULT_RIVER = (0, 255, 255)
COLOR_DEFAULT_OCEAN = (76, 49, 252)
COLOR_DEFAULT_MARSH = (27, 96, 0)
COLOR_DEFAULT_MOUNTAIN = (80, 10, 10,)
COLOR_DEFAULT_DESSERT = (249, 233, 76)

# agent interaction colors
COLOR_DEFAULT_BORDER = (255, 255, 255)
PLAYER_COLOR = (0, 0, 255)

# agent color red, blue, orange, yellow, purple,
AGENT_COLORS = [(0, 0, 255), (255, 0, 0), (255, 165, 0), (255, 255, 0), (128, 0, 128), (0, 255, 0)]


VALUE_DEFAULT_LAND = 0
VALUE_DEFAULT_OCEAN = 1
VALUE_DEFAULT_RIVER = 5
VALUE_DEFAULT_MARSH = 2
VALUE_DEFAULT_MOUNTAIN = 3
VALUE_DEFAULT_DESSERT = 4
LAND = [['land', 10, COLOR_DEFAULT_LAND],
        ['water', 1, COLOR_DEFAULT_OCEAN],
        ['water-adjacent', 1, COLOR_DEFAULT_MARSH],
        ['mountain', 1, COLOR_DEFAULT_MOUNTAIN],
        ['dessert', 1, COLOR_DEFAULT_DESSERT],
        ['river', 1, COLOR_DEFAULT_RIVER]
        ]

# TODO make this in json format
# [ [land_type_name, land_base_value, land_color], ...]

OWNER_DEFAULT_TILE = -1