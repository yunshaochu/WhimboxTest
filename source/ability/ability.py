from source.common.utils.utils import *
from source.interaction.interaction_core import itt
from source.common.utils.img_utils import *
from source.common.utils.posi_utils import *
from source.common.logger import logger
from source.ability.cvar import *
from source.ui.ui import ui_control
from source.ui.page_assets import *

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

        self.ability_keymap = None
        self._initialized = True
    

    def reinit_ability_keymap(self):
        ui_control.ui_goto(page_ability)
        self.ability_keymap = self.get_current_ability_keymap()
        ui_control.ui_goto(page_main)


    def get_current_ability_keymap(self):
        ability_keymap = {}
        cap = itt.capture()
        for i, center in enumerate(ability_icon_centers):
            area = area_offset((-ability_icon_radius, -ability_icon_radius, ability_icon_radius, ability_icon_radius), offset=center)
            img = crop(cap, area)
            lower_white = np.array([0, 0, 230])
            upper_white = np.array([180, 60, 255])
            img = process_with_hsv_threshold(img, lower_white, upper_white)
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
        return ability_keymap

    
    def change_ability(self, ability_name: str, ability_key: str):
        if not is_int(ability_key):
            raise(f'ability_key is not a int: {ability_key}')
        ability_index = int(ability_key) - 1
        if ability_index < 0 or ability_index >= len(ability_icon_centers):
            raise(f'ability_key can only 1~8, but got {ability_key}')

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
        change_success = False
        offset = (AreaAbilityChange.position[0], AreaAbilityChange.position[1])
        last_cap = itt.capture(posi=AreaAbilityChange.position)
        while True:
            text_box_dict = itt.ocr_and_detect_posi(AreaAbilityChange)
            if ability_name in text_box_dict:
                text_center = area_center(text_box_dict[ability_name])
                text_center = (text_center[0] + offset[0], text_center[1] + offset[1])
                click_posi = (text_center[0] + 80, text_center[1] + 80)
                itt.move_and_click(click_posi)
                change_success = True
                break
            itt.middle_scroll(-15)
            time.sleep(0.2)

            # 如果画面不再变化，说明滚到底了，也结束循环
            new_cap = itt.capture(posi=AreaAbilityChange.position)
            rate = similar_img(last_cap, new_cap)
            if rate > 0.99:
                break
            last_cap = new_cap

        if change_success:
            itt.appear_then_click(ButtonAbilitySave)
            return True
        else:
            return False
        

if __name__ == "__main__":
    ability_manager = AbilityManager()
    ability_manager.change_ability(ABILITY_NAME_CLEAR, '8')
