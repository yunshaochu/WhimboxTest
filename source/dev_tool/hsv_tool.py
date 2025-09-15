'''可视化的HSV阈值调节工具'''
import cv2  
import numpy as np  
from source.common.utils.img_utils import *
from source.ui.ui_assets import *

path = "D:\\workspaces\\python\\auto_test\\tools\\snapshot\\jump\\1756804302.9930363.png"

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
    's_max': 50,
    'v_min': 210,
    'v_max': 255,
}
cv2.createTrackbar("Hue Min", "TrackBars", init_data['h_min'], 179, empty)  
cv2.createTrackbar("Hue Max", "TrackBars", init_data["h_max"], 179, empty)  
cv2.createTrackbar("Sat Min", "TrackBars", init_data['s_min'], 255, empty)  
cv2.createTrackbar("Sat Max", "TrackBars", init_data["s_max"], 255, empty)  
cv2.createTrackbar("Val Min", "TrackBars", init_data['v_min'], 255, empty)  
cv2.createTrackbar("Val Max", "TrackBars", init_data['v_max'], 255, empty)  
  
while True:  
    img = cv2.imread(path)
    img = crop(img, AreaMovementWalk.position)
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  
    # 调用回调函数，获取滑动条的值  
    h_min, h_max, s_min, s_max, v_min, v_max = empty(0)  
    lower = np.array([h_min, s_min, v_min])  
    upper = np.array([h_max, s_max, v_max])  
    # 获得指定颜色范围内的掩码  
    mask = cv2.inRange(imgHSV, lower, upper)  
    # 对原图图像进行按位与的操作，掩码区域保留  
    imgResult = cv2.bitwise_and(img, img, mask=mask)  
    # cv2.imwrite("D:\\workspaces\\python\\auto_test\\tools\\snapshot\\jump\\mask.png", mask)
    cv2.imshow("Mask", mask)  
    cv2.imshow("Result", imgResult)  
    cv2.waitKey(1)