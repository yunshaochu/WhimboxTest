# 预计最大移动速度
MOVE_SPEED = 22

# Magic numbers for 1920x1080 desktop
MINIMAP_CENTER = (79 + 102, 20 + 102)
MINIMAP_RADIUS = 102
MINIMAP_POSITION_RADIUS = 100
MINIMAP_POSITION_SCALE = 0.975

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
BIGMAP_POSITION_SCALE = 0.635
