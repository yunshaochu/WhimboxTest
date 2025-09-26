from source.common.cvars import *
from source.ui.ui import ui_control
from source.ui.page_assets import *
from source.interaction.interaction_core import itt
from source.common.utils.img_utils import *
from source.ui.material_icon_assets import material_icon_dict
from source.common.utils.ui_utils import *

import time

material_type_icon_dict = {
    "plant": IconMaterialTypePlant,
    "animal": IconMaterialTypeAnimal,
    "insect": IconMaterialTypeInsect,
    "fish": IconMaterialTypeFish,
    "monster": IconMaterialTypeMonster,
}

class Track:
    def __init__(self):
        self.tracking_material = None

    def change_tracking_material(self, material_name: str):
        '''
        大地图追踪指定材料，用于在小地图上显示附近的材料点位，后续自动寻路去获取
        '''
        if material_name not in material_icon_dict:
            raise Exception(f"不支持追踪{material_name}")
        material_info = material_icon_dict[material_name]
        if not material_info["track"]:
            raise Exception(f"不支持追踪{material_name}")

        material_icon = material_info['icon']
        material_type = material_info['type']
        if material_type not in material_type_icon_dict:
            raise Exception(f"暂不支持追踪{material_type}类型的材料")
        material_type_icon = material_type_icon_dict[material_type]

        # 打开材料追踪窗口
        ui_control.ui_goto(page_bigmap)
        itt.appear_then_click(IconUIBigmap)
        itt.wait_until_stable()

        # 选择材料类别
        result = scroll_find_click(
            AreaBigMapMaterialTypeSelect, 
            material_type_icon, 
            threshold=0.75, 
            hsv_limit=[np.array([0, 0, 230]), np.array([180, 60, 255])])
        if not result:
            raise Exception("材料类别选择失败")
        
        # 选择材料
        time.sleep(0.2) # 等待类别切换完成
        result = scroll_find_click(AreaBigMapMaterialSelect, material_icon, threshold=0.9, scale=0.45)
        if not result:
            raise Exception("材料选择失败")

        # 点击“精确追踪”
        time.sleep(0.2) # 等待一会，避免识别到上一个素材的追踪按钮
        button_text = itt.ocr_single_line(AreaBigMapMaterialTrackConfirm, padding=50)
        if button_text == "精确追踪":
            itt.move_and_click(AreaBigMapMaterialTrackConfirm.center_position())
            itt.wait_until_stable()
            self.tracking_material = material_name
            ui_control.ui_goto(page_main)
            return True
        elif button_text == "取消追踪":
            itt.key_press('esc')
            ui_control.ui_goto(page_main)
        else:
            raise Exception("该材料未开启精确追踪")


if __name__ == "__main__":
    track = Track()
    track.change_tracking_material("玉簪蚂蚱")
    # track.change_tracking_material("插梳鱼")
