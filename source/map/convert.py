import numpy as np
from source.map.detection.cvars import *

class UnknownPositionTypeError(Exception): pass


def convert_InGameMapPx_to_MiralandMAP(points) -> np.ndarray:
    """游戏地图坐标(用于计算屏幕坐标)->图片坐标"""
    points = np.array(points)
    points = points*BIGMAP_POSITION_SCALE
    return points

def convert_MiralandMAP_to_InGameMapPx(points) -> np.ndarray:
    """图片坐标->游戏地图坐标（用于计算屏幕坐标）"""
    points = np.array(points)
    points = points/BIGMAP_POSITION_SCALE
    return points

def convert_gameLoc_to_mapPx(points, decimal=1) -> np.ndarray:
    """游戏原生坐标->图片坐标"""
    points = np.array(points)
    points[0] = points[0] * 0.02222 + 6718
    points[1] = points[1] * 0.02222 + 5587
    points = np.round(points, decimals=decimal)
    return points

def convert_mapPx_to_gameLoc(points, decimal=1) -> np.ndarray:
    """图片坐标->游戏原生坐标"""
    points = np.array(points)
    points[0] = (points[0] - 6718) / 0.02222
    points[1] = (points[1] - 5587) / 0.02222
    points = np.round(points, decimals=decimal)
    return points

if __name__ == '__main__':
    pass