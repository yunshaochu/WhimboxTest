from source.common.cvars import *
from source.ui.ui import ui_control
from source.ui.page_assets import *
from source.interaction.interaction_core import itt
from source.common.utils.img_utils import *
from source.ui.material_icon_assets import material_icon_dict
from source.common.utils.ui_utils import *
from source.map.map import nikki_map, MINIMAP_RADIUS
from source.view_and_move.utils import *
from source.ability.cvar import *

import time

material_type_icon_dict = {
    "plant": IconMaterialTypePlant,
    "animal": IconMaterialTypeAnimal,
    "insect": IconMaterialTypeInsect,
    "fish": IconMaterialTypeFish,
    "monster": IconMaterialTypeMonster,
}

material_type_to_ability_name = {
    "animal": ABILITY_NAME_ANIMAL,
    "insect": ABILITY_NAME_INSECT,
}

class Track:
    def __init__(self):
        self.tracking_material = None

    def change_tracking_material(self, material_name: str):
        '''
        大地图追踪指定材料，用于在小地图上显示附近的材料点位，后续自动寻路去获取
        '''

        if self.tracking_material == material_name:
            return
        
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
        result = scroll_find_click(AreaBigMapMaterialSelect, material_icon, threshold=0.8, scale=0.45)
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

    def get_material_track_degree(self):
        '''根据小地图，计算材料与玩家之间的角度'''
        cap = itt.capture()
        minimap_img = nikki_map._get_minimap(cap, MINIMAP_RADIUS)
        lower = np.array([13, 90, 160])
        upper = np.array([15, 200, 255])
        minimap_hsv = process_with_hsv_limit(minimap_img, lower, upper)
        minimap_blur = cv2.GaussianBlur(minimap_hsv, (3, 3), 1)

        circles = cv2.HoughCircles(
            minimap_blur,
            cv2.HOUGH_GRADIENT,
            dp=1,          # 累加器分辨率（可调 1.0~1.5）
            minDist=10,      # 圆心最小间距，建议≈ 2*minRadius - 些许
            param1=100,      # Canny高阈值
            param2=9,       # 累加器阈值，越小越容易出圆（可调 8~18）
            minRadius=14,
            maxRadius=16
        )
        
        if circles is not None:
            minimap_center = (MINIMAP_RADIUS, MINIMAP_RADIUS)
            min_dist = 99999
            for x, y, r in circles[0, :]:
                dist = euclidean_distance(minimap_center, (x, y))
                if dist < min_dist:
                    min_dist = dist
                    closest_circle = (x, y, r)
            
            if CV_DEBUG_MODE:
                print(min_dist)
                x, y, r = np.uint16(np.around(closest_circle))
                cv2.circle(minimap_img, (x, y), r, (0, 0, 255), 2)
                cv2.circle(minimap_img, (x, y), 2, (0, 0, 255), 3)
                cv2.imshow("minimap_img", minimap_img)
                cv2.waitKey(1)
            
            # 如果材料出现在小地图边缘，说明附近已经没有材料了
            if min_dist > MINIMAP_RADIUS - 20:
                return None
            else:
                degree = calculate_posi2degree(minimap_center, closest_circle[0:2])
                return degree
        return None

    def check_tracking_near(self):
        '''判断是否已经靠近材料（已废弃，改用is_ability_active判断）'''
        img = itt.capture(AreaMaterialTrackNear.position)
        if CV_DEBUG_MODE:
            img_copy = img.copy()
        lower = np.array([17, 140, 130])
        upper = np.array([20, 180, 200])
        mask = process_with_hsv_limit(img, lower, upper)
        circles = cv2.HoughCircles(
            mask,
            cv2.HOUGH_GRADIENT,
            dp=1.2,          # 累加器分辨率（可调 1.0~1.5）
            minDist=22,      # 圆心最小间距，建议≈ 2*minRadius - 些许
            param1=120,      # Canny高阈值
            param2=10,       # 累加器阈值，越小越容易出圆（可调 8~18）
            minRadius=16,
            maxRadius=18
        )
        if circles is not None:
            if CV_DEBUG_MODE:
                for circle in circles[0, :]:
                    x, y, r = np.uint16(np.around(circle))
                    cv2.circle(img_copy, (x, y), r, (0, 0, 255), 2)
                    cv2.circle(img_copy, (x, y), 2, (0, 0, 255), 3)
                cv2.imshow("track_near_img", img_copy)
                cv2.waitKey(1)
            return True
        return False
    
    def is_ability_active(self):
        '''
        判断能力是否激活，通过判断能力按钮外圈是否发光，来判断是否可以使用能力了
        '''
        img = itt.capture(AreaAbilityButton.position)
        lower = np.array([0, 80, 240])
        upper = np.array([30, 110, 255])
        mask = process_with_hsv_limit(img, lower, upper)
        px_count = cv2.countNonZero(mask)
        if px_count > 200:
            return True
        return False

material_track = Track()

if __name__ == "__main__":
    CV_DEBUG_MODE = True
    material_track.change_tracking_material("发卡蚱蜢")
    # while True:
    #     material_track.get_material_track_degree()
    #     time.sleep(0.2)
