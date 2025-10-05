from whimbox.common.utils.posi_utils import *

config = {
    "view_rotation_ratio": 1, # 视角旋转比例, 转动角度*比例=鼠标移动像素，会动态修改
}


def angle2movex(angle):
    px = angle * config["view_rotation_ratio"]
    return int(px)


def calculate_posi2degree(curr_posi, target_posi):
    """计算两点之间的角度"""
    degree = points_angle(curr_posi, target_posi, coordinate=ANGLE_NEGATIVE_Y)
    if abs(degree) < 1:
        return 0
    if math.isnan(degree):
        degree = 0
    return degree


def calculate_delta_angle(cangle, tangle):
    """计算两个角度之间的差值"""
    dangle = (cangle - tangle) % 360
    if dangle > 180:
        dangle = -(360 - dangle)
    elif dangle < -180:
        dangle = (360 + dangle)
    return dangle


