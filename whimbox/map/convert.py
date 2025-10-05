import numpy as np
from whimbox.map.detection.cvars import *

class UnknownPositionTypeError(Exception): pass


def convert_InGameMapPx_to_PngMapPx(points, map_name) -> np.ndarray:
    """游戏地图坐标(屏幕坐标)->图片地图坐标"""
    points = np.array(points)
    points = points * BIGMAP_POSITION_SCALE_DICT[map_name]
    return points

def convert_PngMapPx_to_InGameMapPx(points, map_name) -> np.ndarray:
    """图片地图坐标->游戏地图坐标（屏幕坐标）"""
    points = np.array(points)
    points = points / BIGMAP_POSITION_SCALE_DICT[map_name]
    return points

def convert_GameLoc_to_PngMapPx(points, map_name, decimal=1) -> np.ndarray:
    """游戏原生坐标->图片坐标"""
    points = np.array(points)
    points[0] = points[0] * GAMELOC_TO_PNGMAP_SCALE + GAMELOC_TO_PNGMAP_OFFSET_DICT[map_name][0]
    points[1] = points[1] * GAMELOC_TO_PNGMAP_SCALE + GAMELOC_TO_PNGMAP_OFFSET_DICT[map_name][1]
    points = np.round(points, decimals=decimal)
    return points

def convert_PngMapPx_to_GameLoc(points, map_name, decimal=1) -> np.ndarray:
    """图片坐标->游戏原生坐标"""
    points = np.array(points)
    points[0] = (points[0] - GAMELOC_TO_PNGMAP_OFFSET_DICT[map_name][0]) / GAMELOC_TO_PNGMAP_SCALE
    points[1] = (points[1] - GAMELOC_TO_PNGMAP_OFFSET_DICT[map_name][1]) / GAMELOC_TO_PNGMAP_SCALE
    points = np.round(points, decimals=decimal)
    return points

if __name__ == '__main__':
    pass