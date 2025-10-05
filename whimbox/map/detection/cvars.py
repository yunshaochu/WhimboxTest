PROVINCE_NAMES = [
    "心愿原野",
    "星海",
    "家园",
]

MAP_NAME_MIRALAND = "miraland"
MAP_NAME_STARSEA = "starsea"
MAP_NAME_HOME = "home"

REGION_NAME_TO_MAP_NAME_DICT = {
    MAP_NAME_STARSEA: ["星海"],
    MAP_NAME_MIRALAND: ["纪念山地", "花愿镇", "微风绿野", "小石树田村", "石树田无人区", "祈愿树林"]
}

GAMELOC_TO_PNGMAP_SCALE = 0.02222
GAMELOC_TO_PNGMAP_OFFSET_DICT = {
    MAP_NAME_MIRALAND: (6718, 5587),
    MAP_NAME_STARSEA: (2447, 1046),
}

# 预计最大移动速度
MOVE_SPEED = 22

# Magic numbers for 1920x1080 desktop
MINIMAP_CENTER = (79 + 102, 20 + 102)
MINIMAP_RADIUS = 102
MINIMAP_POSITION_RADIUS = 100
MINIMAP_POSITION_SCALE_DICT = {
    MAP_NAME_MIRALAND: 0.975,
    MAP_NAME_STARSEA: 0.8,
}

# Downscale png map and minimap for faster run
POSITION_SEARCH_SCALE = 0.5
# Search the area that is 1.3x minimap
POSITION_SEARCH_RADIUS = 1.3
# Can't figure out why but the result_of_0.5_lookup_scale + 0.5 ~= result_of_1.0_lookup_scale
POSITION_MOVE = (0.5, 0.5)

DIRECTION_SIMILARITY_COLOR = (155, 255, 255)
# Radius to search direction arrow, about 15px
DIRECTION_RADIUS = 13
# Downscale direction arrows for faster run
DIRECTION_SEARCH_SCALE = 0.5
# Scale to png
DIRECTION_ROTATION_SCALE = 1.0

# Downscale png map to run faster
BIGMAP_SEARCH_SCALE = 0.125
# Magic number that resize a 1920*1080 screenshot to luma_05x_png
BIGMAP_POSITION_SCALE_DICT = {
    MAP_NAME_MIRALAND: 0.637,
    MAP_NAME_STARSEA: 0.62,
}
