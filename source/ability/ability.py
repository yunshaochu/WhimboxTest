from source.common.utils.utils import *
from source.interaction.interaction_core import itt
from source.common.utils.img_utils import *
from source.common.utils.posi_utils import *
from source.common.logger import logger
from source.ability.cvar import *
from source.ui.ui import ui_control
from source.ui.page_assets import *
from source.common.utils.ui_utils import *

import time


class AbilityManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AbilityManager, cls).__new__(cls)
        return cls._instance


    def __init__(self):
        if self._initialized:
            return

        self.current_ability = None
        self.ability_keymap = None
        self.jump_ability = None
        self.battle_ability = None
        self._initialized = True


    def _get_ability_hsv_icon(self, center, cap):
        area = area_offset((-ability_icon_radius, -ability_icon_radius, ability_icon_radius, ability_icon_radius), offset=center)
        img = crop(cap, area)
        lower_white = np.array([0, 0, 230])
        upper_white = np.array([180, 60, 255])
        img = process_with_hsv_threshold(img, lower_white, upper_white)
        return img


    def _check_jump_ability(self):
        cap = itt.capture()
        img = self._get_ability_hsv_icon(jump_ability_center, cap)
        for icon in jump_ability_hsv_icons:
            rate = similar_img(img, icon.image[:, :, 0], ret_mode=IMG_RATE)
            if rate > 0.92:
                ability_name = icon_name_to_ability_name.get(icon.name, None)
                if ability_name is not None:
                    self.jump_ability = ability_name
                    return True
        logger.error(f'unknown jump ability icon')
        return False


    def _check_ability_keymap(self):
        ability_keymap = {}
        cap = itt.capture()
        for i, center in enumerate(ability_icon_centers):
            img = self._get_ability_hsv_icon(center, cap)
            for icon in ability_hsv_icons:
                rate = similar_img(img, icon.image[:, :, 0], ret_mode=IMG_RATE)
                if rate > 0.92:
                    logger.debug(f'{icon.name} rate: {rate}')
                    ability_name = icon_name_to_ability_name.get(icon.name, None)
                    if ability_name is None:
                        logger.error(f'unknown ability icon: {icon.name}')
                    else:
                        ability_keymap[ability_name] = str(i+1)
                    break
        self.ability_keymap = ability_keymap
        return True

    
    def set_ability(self, ability_name: str, ability_key: str):
        '''
        切换能力
        
        Args:
            ability_name: 能力名称，只能使用cvar中的ABILITY_NAME_XXX
            ability_key: 能力键位，只支持1~8和jump
        '''

        # 参数校验
        if ability_key != 'jump':
            if not is_int(ability_key):
                raise(f'ability_key is not a int: {ability_key}')
            ability_index = int(ability_key) - 1
            if ability_index < 0 or ability_index >= len(ability_icon_centers):
                raise(f'ability_key can only 1~8, but got {ability_key}')

        # 获取当前能力配置
        if self.jump_ability is None:
            ui_control.ui_goto(page_ability)
            self._check_jump_ability()
        if self.ability_keymap is None:
            ui_control.ui_goto(page_ability)
            self._check_ability_keymap()

        # 检查当前能力配置是否已经满足要求
        if ability_key == 'jump':
            if self.jump_ability == ability_name:
                ui_control.ui_goto(page_main)
                return True
        else:
            if self.ability_keymap.get(ability_name, None) == ability_key:
                ui_control.ui_goto(page_main)
                return True

        # 开始配置能力
        if ability_key == 'jump':
            target_ability_icon_center = jump_ability_center
        else:
            target_ability_icon_center = ability_icon_centers[ability_index]
        itt.move_and_click(target_ability_icon_center)
        time.sleep(0.2)
        itt.move_to(AreaAbilityChange.center_position())
        # 一直向上滚到头，直到画面不再变化
        last_cap = itt.capture(posi=AreaAbilityChange.position)
        while True:
            itt.middle_scroll(15)
            time.sleep(0.2)
            new_cap = itt.capture(posi=AreaAbilityChange.position)
            rate = similar_img(last_cap, new_cap)
            # logger.debug(f'rate: {rate}')
            if rate > 0.99:
                break
            last_cap = new_cap
        
        # 向下滚动，寻找指定的ability_name
        res = scroll_find_click(AreaAbilityChange, ability_name, click_offset=(80, 80))
        if res:
            itt.appear_then_click(ButtonAbilitySave)
            if ability_key == 'jump':
                self.jump_ability = ability_name
            else:
                self.ability_keymap[ability_name] = ability_key

        ui_control.ui_goto(page_main)
        return res

    def change_ability(self, ability_name: str):
        # 如果当前能力已经符合，就直接返回
        if self.current_ability == ability_name:
            return True
        # 检查能力配置是否已初始化
        if self.ability_keymap is None:
            ui_control.ui_goto(page_ability)
            self._check_ability_keymap()
        # 检查目标能力是否已配置
        key = self.ability_keymap.get(ability_name, None)
        if key is None:
            # 如果没配置，默认配置到键位8
            if self.set_ability(ability_name, '8'):
                key = '8'

        ui_control.ui_goto(page_main)
        if key:
            itt.key_press(key)
            self.current_ability = ability_name
            return True
        else:
            return False
        

ability_manager = AbilityManager()


if __name__ == "__main__":
    ability_manager.change_ability(ABILITY_NAME_INSECT)
