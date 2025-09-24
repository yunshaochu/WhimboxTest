from source.ui.ui_assets import *

# 能力配置界面，能力图标半径
ability_icon_radius = 40
# 能力配置界面，8个能力图标中心点
ability_icon_centers = [
    (1099, 277), (1192, 437), (1193, 627), (1099, 789),
    (587, 788), (493, 625), (493, 438), (587, 276)
]
# hsv处理后的能力图标，用于匹配
ability_hsv_icons = [IconAbilityClear, IconAbilityBug, IconAbilityFish, IconAbilityFly, IconAbilitySmall]

ABILITY_NAME_CLEAR = '动物清洁'
ABILITY_NAME_BUG = '捕虫'
ABILITY_NAME_FISH = '钓鱼'
ABILITY_NAME_FLY = '滑翔'
ABILITY_NAME_SMALL = '变小'

icon_name_to_ability_name = {
    'IconAbilityClear': ABILITY_NAME_CLEAR,
    'IconAbilityBug': ABILITY_NAME_BUG,
    'IconAbilityFish': ABILITY_NAME_FISH,
    'IconAbilityFly': ABILITY_NAME_FLY,
    'IconAbilitySmall': ABILITY_NAME_SMALL,
}