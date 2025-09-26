'''通用的游戏UI操作工具'''

from source.ui.template.img_manager import GameImg, ImgIcon
from source.ui.template.button_manager import Button
from source.ui.template.text_manager import Text
from source.ui.template.posi_manager import Area
from source.interaction.interaction_core import itt
from source.common.utils.img_utils import *
from source.common.utils.posi_utils import *

import time


def find_game_img(game_img: GameImg, cap, threshold, scale=0.5):
    # 准备需要匹配的两张图片
    template = game_img.raw_image
    if template.shape[2] == 4:
        template_rgb = template[:, :, :3]
        alpha = template[:, :, 3]
        mask = (alpha > 128).astype(np.uint8) * 255  # 透明区域设为0，不参与检测
    else:
        template_rgb = template
        mask = None

    if scale:
        template_rgb = cv2.resize(template_rgb, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
        if mask is not None:
            mask = cv2.resize(mask, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)

    if CV_DEBUG_MODE:
        # 将template_rgb的mask区域显示为黑色，用cv2显示出来
        template_show = template_rgb.copy()
        template_show[mask == 0] = 0
        cv2.imshow("template", template_show)
        cv2.waitKey(0)
    
    # 模板匹配
    res = cv2.matchTemplate(cap, template_rgb, cv2.TM_CCOEFF_NORMED, mask=mask)

    # 找到最大匹配位置
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    # 在目标图上绘制矩形
    th, tw = template_rgb.shape[:2]
    top_left = max_loc
    bottom_right = (top_left[0] + tw, top_left[1] + th)

    if CV_DEBUG_MODE:
        print(f"max_val: {max_val}, threshold: {threshold}")
        cap_copy = cap.copy()
        cv2.rectangle(cap_copy, top_left, bottom_right, (0,255,0), 3)
        cv2.imshow("Detected", cap_copy)
        cv2.waitKey(0)
    
    if max_val < threshold:
        return None

    box = [top_left[0], top_left[1], bottom_right[0], bottom_right[1]]
    return box

def scroll_find_click(area: Area, target, threshold=0, hsv_limit=None, scale=0, click_offset=(0, 0)) -> bool:
    '''
    在指定的区域内滚动，寻找并点击目标

    Args:
        area: 目标区域
        target: 寻找的目标，ImgIcon或GameImg或str
        threshold: 相似度阈值, 用于ImgIcon和GameImg
        hsv_limit: hsv上下限，用于ImgIcon，如[np.array([0, 0, 230]), np.array([180, 60, 255])]
        scale: target的缩放比例，用于ImgIcon或GameImg
        click_offset: 点击偏移量，tuple(x, y)
    
    Returns:
        bool: 是否找到目标
    '''
    box = None
    cap = itt.capture(posi = area.position)
    while True:
        if isinstance(target, ImgIcon):
            target_img = target.image
            if hsv_limit:
                if scale:
                    target_img = cv2.resize(target_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
                target_img = target_img[:, :, 0]
                cap_hsv = process_with_hsv_threshold(cap, hsv_limit[0], hsv_limit[1])
                rate, loc = similar_img(cap_hsv, target_img, ret_mode=IMG_RECT)
            else:
                if scale:
                    target_img = cv2.resize(target_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
                rate, loc = similar_img(cap, target_img, ret_mode=IMG_RECT)

            if rate > threshold:
                th, tw = target_img.shape[:2]
                top_left = loc
                bottom_right = (top_left[0] + tw, top_left[1] + th)
                if CV_DEBUG_MODE:
                    print(f"rate: {rate}, threshold: {threshold}")
                    cap_copy = cap.copy()
                    cv2.rectangle(cap_copy, top_left, bottom_right, (0, 255, 0), 2)
                    cv2.imshow("Detected", cap_copy)
                    cv2.waitKey(0)
                box = [top_left[0], top_left[1], bottom_right[0], bottom_right[1]]
                break

        elif isinstance(target, GameImg):
            box = find_game_img(target, cap, threshold, scale)
            if box:
                break
        
        elif isinstance(target, str):
            text_box_dict = itt.ocr_and_detect_posi(area)
            if target in text_box_dict:
                box = text_box_dict[target]
                break
        
        else:
            raise Exception(f"不支持的target类型: {type(target)}")

        # 如果没找到目标，就把鼠标移到area的右下角，向下滚动
        scroll_posi = (area.position[2], area.position[3])
        itt.move_to(scroll_posi)
        itt.middle_scroll(-15)
        time.sleep(0.2)

        # 如果画面不再变化，说明滚到头了
        new_cap = itt.capture(posi = area.position)
        rate = similar_img(cap, new_cap)
        if rate > 0.99:
            break
        else:
            cap = new_cap
        
    if box:
        center = area_center(box)
        click_posi = (
            area.position[0] + center[0] + click_offset[0], 
            area.position[1] + center[1] + click_offset[1]
        )
        itt.move_and_click(click_posi)
        return True
    else:
        return False

    
def wait_until_appear_then_click(obj, retry_time=3):
    while retry_time > 0:
        if isinstance(obj, Button):
            if itt.appear_then_click(obj):
                return True
        else:
            return False
        retry_time -= 1
        time.sleep(1)
    return False


def wait_until_appear(obj, retry_time=3):
    while retry_time > 0:
        if isinstance(obj, ImgIcon):
            if itt.get_img_existence(obj):
                return True
        elif isinstance(obj, Text):
            if itt.get_text_existence(obj):
                return True
        else:
            return False
        retry_time -= 1
        time.sleep(1)
    return False


            
if __name__ == "__main__":
    CV_DEBUG_MODE = True
    from source.ui.ui_assets import *
    from source.ui.material_icon_assets import material_icon_dict
    # target = material_icon_dict["玉簪蚂蚱"]["icon"]
    # cap = itt.capture(posi=AreaBigMapMaterialSelect.position)
    # find_game_img(target, cap, threshold=0.7, scale=0.41)

    hsv_limit = [np.array([0, 0, 100]), np.array([180, 60, 255])]
    # scroll_find_click(AreaDigMainTypeSelect, IconMaterialTypeMonster, threshold=0.85, hsv_limit=hsv_limit, scale=1.233)
    scroll_find_click(AreaDigSubTypeSelect, IconMaterialTypeInsect, threshold=0.85, hsv_limit=hsv_limit, scale=0.83)