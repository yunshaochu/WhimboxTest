from source.interaction.interaction_core import itt
import time
from source.ui.template import img_manager, text_manager, button_manager, posi_manager
import cv2
import numpy as np

def wait_until_appear_then_click(obj, retry_time=3):
    while retry_time > 0:
        if isinstance(obj, button_manager.Button):
            if itt.appear_then_click(obj):
                return True
        else:
            return False
        retry_time -= 1
        time.sleep(1)
    return False

def wait_until_appear(obj, retry_time=3):
    while retry_time > 0:
        if isinstance(obj, img_manager.ImgIcon):
            if itt.get_img_existence(obj):
                return True
        elif isinstance(obj, text_manager.Text):
            if itt.get_text_existence(obj):
                return True
        else:
            return False
        retry_time -= 1
        time.sleep(1)
    return False

def find_game_img_in_area(game_img: img_manager.GameImg, area: posi_manager.Area, scale=0.5, show=False):
    # pt = time.time()
    # 准备需要匹配的两张图片
    template = game_img.copy().raw_image
    if template.shape[2] == 4:
        template_rgb = template[:, :, :3]
        alpha = template[:, :, 3]
        mask = (alpha > 128).astype(np.uint8) * 255  # 透明区域设为0，不参与检测
    else:
        template_rgb = template
        mask = None

    if scale != 1.0:
        template_rgb = cv2.resize(template_rgb, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
        if mask is not None:
            mask = cv2.resize(mask, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)

    if show:
        # 将template_rgb的mask区域显示为白色，用cv2显示出来
        template_show = template_rgb.copy()
        template_show[mask == 0] = 0
        cv2.imshow("template", template_show)
        cv2.waitKey(0)

    target = itt.capture(area.position)
    if show:
        cv2.imshow("target", target)
        cv2.waitKey(0)
    
    # 模板匹配
    res = cv2.matchTemplate(target, template_rgb, cv2.TM_CCOEFF_NORMED, mask=mask)

    # 找到最大匹配位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # print(f"最佳匹配位置: {max_loc}, 置信度: {max_val:.3f}")
    if max_val < game_img.threshold:
        return None, max_val

    # 在目标图上绘制矩形
    th, tw = template_rgb.shape[:2]
    top_left = max_loc
    bottom_right = (top_left[0] + tw, top_left[1] + th)

    # print(f"耗时: {time.time()-pt:.3f}s")

    if show:
        matched = target.copy()
        cv2.rectangle(matched, top_left, bottom_right, (0,255,0), 3)
        cv2.imshow("Detected", matched)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    position = [
        area.position[0] + top_left[0], 
        area.position[1] + top_left[1], 
        area.position[0] + bottom_right[0], 
        area.position[1] + bottom_right[1]
    ]
    return position, max_val
    # return top_left, bottom_right, max_val



if __name__ == "__main__":
    from source.assets.ui import *
    print(find_game_img_in_area(T_UI_icon_004, AreaUIDigItemSelect, scale=0.46, show=True))