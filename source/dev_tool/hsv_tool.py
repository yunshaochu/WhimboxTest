'''可视化的HSV阈值调节工具'''
import cv2  
import numpy as np  
from source.common.utils.img_utils import *
from source.ui.ui_assets import *

# 滑动条的回调函数，获取滑动条位置处的值  
def empty(a):  
    h_min = cv2.getTrackbarPos("Hue Min", "TrackBars")  
    h_max = cv2.getTrackbarPos("Hue Max", "TrackBars")  
    s_min = cv2.getTrackbarPos("Sat Min", "TrackBars")  
    s_max = cv2.getTrackbarPos("Sat Max", "TrackBars")  
    v_min = cv2.getTrackbarPos("Val Min", "TrackBars")  
    v_max = cv2.getTrackbarPos("Val Max", "TrackBars")  
    # print(h_min, h_max, s_min, s_max, v_min, v_max)  
    return h_min, h_max, s_min, s_max, v_min, v_max  
    
# 创建一个窗口，放置6个滑动条  
cv2.namedWindow("TrackBars")  
cv2.resizeWindow("TrackBars", 640, 300)  
init_data = {
    'h_min': 0,
    'h_max': 180,
    's_min': 0,
    's_max': 60,
    'v_min': 230,
    'v_max': 255,
}
cv2.createTrackbar("Hue Min", "TrackBars", init_data['h_min'], 179, empty)  
cv2.createTrackbar("Hue Max", "TrackBars", init_data["h_max"], 179, empty)  
cv2.createTrackbar("Sat Min", "TrackBars", init_data['s_min'], 255, empty)  
cv2.createTrackbar("Sat Max", "TrackBars", init_data["s_max"], 255, empty)  
cv2.createTrackbar("Val Min", "TrackBars", init_data['v_min'], 255, empty)  
cv2.createTrackbar("Val Max", "TrackBars", init_data['v_max'], 255, empty)  

if __name__ == "__main__" and True:
    while True:
        path = "D:\\workspaces\\python\\Whimbox\\assets\\imgs\\Windows\\BigMap\\common\\IconBigMapMaterialTrackTypePlant_bk.png"
        # path = "D:\\workspaces\\python\\Whimbox\\assets\\imgs\\Windows\\BigMap\\common\\AreaBigMapMaterialTypeSelect.png"
        img = cv2.imread(path)
        # from source.interaction.interaction_core import itt
        # img = itt.capture(posi = AreaWardrobeAbility1.position)
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  
        # 调用回调函数，获取滑动条的值  
        h_min, h_max, s_min, s_max, v_min, v_max = empty(0)  
        lower = np.array([h_min, s_min, v_min])  
        upper = np.array([h_max, s_max, v_max])  
        # 获得指定颜色范围内的掩码  
        mask = cv2.inRange(imgHSV, lower, upper)
        img = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        save_image(img, f'D:\\workspaces\\python\\Whimbox\\tools\\hsv_tool\\IconBigMapMaterialTrackTypePlant.png')
        cv2.imshow("Mask", mask)
        cv2.waitKey(1)
        

if __name__ == "__main__" and False:
    from source.interaction.interaction_core import itt
    from source.common.utils.posi_utils import *
    ability_icon_radius = 40
    jump_ability_center = (228, 625)
    while True:
        cap = itt.capture()
        img = crop(cap, area_offset((-ability_icon_radius, -ability_icon_radius, ability_icon_radius, ability_icon_radius), offset=jump_ability_center))
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  
        # 调用回调函数，获取滑动条的值  
        h_min, h_max, s_min, s_max, v_min, v_max = empty(0)  
        lower = np.array([h_min, s_min, v_min])  
        upper = np.array([h_max, s_max, v_max])  
        mask = cv2.inRange(imgHSV, lower, upper)  
        imgResult = cv2.bitwise_and(img, img, mask=mask)
        cv2.imshow("Mask", mask)  
        cv2.imshow("Result", imgResult)  
        key =cv2.waitKey(1)
        if key == 27:  # ESC键退出
            img = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            save_image(img, f'D:\\workspaces\\python\\Whimbox\\tools\\hsv_tool\\jump2.png')
            break


if __name__ == "__main__" and False:
    from source.interaction.interaction_core import itt
    from source.common.utils.posi_utils import *
    ability_icon_radius = 40
    ability_icon_centers = [
        (1099, 277), (1192, 437), (1193, 627), (1099, 789),
        (587, 788), (493, 625), (493, 438), (587, 276)
    ]

    while True:
        cap = itt.capture()
        processed_images = []
        
        # 调用回调函数，获取滑动条的值  
        h_min, h_max, s_min, s_max, v_min, v_max = empty(0)  
        lower = np.array([h_min, s_min, v_min])  
        upper = np.array([h_max, s_max, v_max])
        
        # 处理每个图标
        for center in ability_icon_centers:
            area = area_offset((-ability_icon_radius, -ability_icon_radius, ability_icon_radius, ability_icon_radius), offset=center)
            img = crop(cap, area)
            processed = process_with_hsv_threshold(img, lower, upper)
            # 转换为彩色图像以便拼接
            processed_color = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
            processed_images.append(processed_color)
        
        # 创建拼接图像
        # 2行4列布局
        rows = 2
        cols = 4
        cell_height = ability_icon_radius * 2
        cell_width = ability_icon_radius * 2
        padding = 10  # 图像间的间距
        
        # 创建空白画布
        canvas_height = rows * cell_height + (rows - 1) * padding
        canvas_width = cols * cell_width + (cols - 1) * padding
        canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
        
        # 将处理后的图像放入画布
        for i, img in enumerate(processed_images):
            row = i // cols
            col = i % cols
            y_start = row * (cell_height + padding)
            x_start = col * (cell_width + padding)
            canvas[y_start:y_start+cell_height, x_start:x_start+cell_width] = img
        
        # 显示原始图像和HSV处理后的拼接图像
        cv2.imshow('HSV Processed Icons', canvas)
        key = cv2.waitKey(100)
        if key == 27:  # ESC键退出
            for i, img in enumerate(processed_images):
                save_image(img, f'D:\\workspaces\\python\\Whimbox\\tools\\hsv_tool\\{i+1}.png')
            break