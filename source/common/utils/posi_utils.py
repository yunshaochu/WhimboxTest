import math
import numpy as np

from source.common.cvars import *
from source.common.utils.utils import random_normal_distribution_int


def points_angle(p1, target_posi, coordinate=ANGLE_NORMAL):
    """计算两点间角度.

    Args:
        p1 (_type_): _description_
        p2 (_type_): _description_
        coordinate (_type_, optional): _description_. Defaults to ANGLE_NORMAL.

    Returns:
        _type_: _description_
    """
    # p1: current point
    # p2: target point
    x = p1[0]
    y = p1[1]
    tx = target_posi[0]
    ty = target_posi[1]
    if coordinate == ANGLE_NEGATIVE_Y:
        y = -y
        ty = -ty
    if abs((tx - x)) <= 0.05: # in case of dividing by zero
        tx = 0.05
        x = 0
    k = (ty - y) / (tx - x)
    degree = math.degrees(math.atan(k))
    if degree < 0:
        degree += 180
    if ty < y:
        degree += 180

    degree -= 90
    if degree > 180:
        degree -= 360
    return degree

def add_angle(angle, delta):
    if DEBUG_MODE:
        print(f"add angle: {angle}+{delta}", end='=')
    angle+=delta
    if angle > 180:
        angle -= 360
    if angle < -180:
        angle += 360
    if DEBUG_MODE:
        print(angle)
    return angle


def area_offset(area, offset):
    """
    Move an area.

    Args:
        area: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y).
        offset: (x, y).

    Returns:
        tuple: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y).
    """
    upper_left_x, upper_left_y, bottom_right_x, bottom_right_y = area
    x, y = offset
    return upper_left_x + x, upper_left_y + y, bottom_right_x + x, bottom_right_y + y


def area_pad(area, pad=10):
    """
    Inner offset an area.

    Args:
        area: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y).
        pad (int):

    Returns:
        tuple: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y).
    """
    upper_left_x, upper_left_y, bottom_right_x, bottom_right_y = area
    return upper_left_x + pad, upper_left_y + pad, bottom_right_x - pad, bottom_right_y - pad


def limit_in(x, lower, upper):
    """
    Limit x within range (lower, upper)

    Args:
        x:
        lower:
        upper:

    Returns:
        int, float:
    """
    return max(min(x, upper), lower)


def area_limit(area1, area2):
    """
    Limit an area in another area.

    Args:
        area1: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y).
        area2: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y).

    Returns:
        tuple: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y).
    """
    x_lower, y_lower, x_upper, y_upper = area2
    return (
        limit_in(area1[0], x_lower, x_upper),
        limit_in(area1[1], y_lower, y_upper),
        limit_in(area1[2], x_lower, x_upper),
        limit_in(area1[3], y_lower, y_upper),
    )


def area_size(area):
    """
    Area size or shape.

    Args:
        area: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y).

    Returns:
        tuple: (x, y).
    """
    return (
        max(area[2] - area[0], 0),
        max(area[3] - area[1], 0)
    )


def area_center(area):
    """
    Get the center of an area

    Args:
        area: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y)

    Returns:
        tuple: (x, y)
    """
    x1, y1, x2, y2 = area
    return (x1 + x2) / 2, (y1 + y2) / 2


def point_limit(point, area):
    """
    Limit point in an area.

    Args:
        point: (x, y).
        area: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y).

    Returns:
        tuple: (x, y).
    """
    return (
        limit_in(point[0], area[0], area[2]),
        limit_in(point[1], area[1], area[3])
    )


def point_in_area(point, area, threshold=5):
    """

    Args:
        point: (x, y).
        area: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y).
        threshold: int

    Returns:
        bool:
    """
    return area[0] - threshold < point[0] < area[2] + threshold and area[1] - threshold < point[1] < area[3] + threshold


def area_in_area(area1, area2, threshold=5):
    """

    Args:
        area1: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y).
        area2: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y).
        threshold: int

    Returns:
        bool:
    """
    return area2[0] - threshold <= area1[0] \
        and area2[1] - threshold <= area1[1] \
        and area1[2] <= area2[2] + threshold \
        and area1[3] <= area2[3] + threshold


def area_cross_area(area1, area2, threshold=5):
    """

    Args:
        area1: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y).
        area2: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y).
        threshold: int

    Returns:
        bool:
    """
    # https://www.yiiven.cn/rect-is-intersection.html
    xa1, ya1, xa2, ya2 = area1
    xb1, yb1, xb2, yb2 = area2
    return abs(xb2 + xb1 - xa2 - xa1) <= xa2 - xa1 + xb2 - xb1 + threshold * 2 \
        and abs(yb2 + yb1 - ya2 - ya1) <= ya2 - ya1 + yb2 - yb1 + threshold * 2


def linspace(point1, point2, num_points=5):
    """获取两个点之间的n等分点"""
    x_points = np.linspace(point1[0], point2[0], num_points)
    y_points = np.linspace(point1[1], point2[1], num_points)
    # 将x和y坐标合并成一个数组
    points = np.array([x_points, y_points]).T
    return points


def euclidean_distance(p1, p2):
    """计算两点间欧氏距离.

    Args:
        p1 (_type_): _description_
        p2 (_type_): _description_

    Returns:
        _type_: _description_
    """
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def euclidean_distance_plist(p1, plist) -> np.ndarray:
    """计算点与一系列点间欧氏距离.

    Args:
        p1 (_type_): _description_
        plist (_type_): _description_

    Returns:
        np.ndarray: p1到plist的距离列表.
    """
    if not isinstance(p1, np.ndarray):
        p1 = np.array(p1)
    if not isinstance(plist, np.ndarray):
        plist = np.array(plist)
    return np.sqrt((p1[0] - plist[:,0]) ** 2 + (p1[1] - plist[:,1]) ** 2)


def random_rectangle_point(area, n=3):
    """Choose a random point in an area.

    Args:
        area: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y).
        n (int): The amount of numbers in simulation. Default to 3.

    Returns:
        tuple(int): (x, y)
    """
    x = random_normal_distribution_int(area[0], area[2], n=n)
    y = random_normal_distribution_int(area[1], area[3], n=n)
    return x, y


def random_rectangle_vector(vector, box, random_range=(0, 0, 0, 0), padding=15):
    """Place a vector in a box randomly.

    Args:
        vector: (x, y)
        box: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y).
        random_range (tuple): Add a random_range to vector. (x_min, y_min, x_max, y_max).
        padding (int):

    Returns:
        tuple(int), tuple(int): start_point, end_point.
    """
    vector = np.array(vector) + random_rectangle_point(random_range)
    vector = np.round(vector).astype(int)
    half_vector = np.round(vector / 2).astype(int)
    box = np.array(box) + np.append(np.abs(half_vector) + padding, -np.abs(half_vector) - padding)
    center = random_rectangle_point(box)
    start_point = center - half_vector
    end_point = start_point + vector
    return tuple(start_point), tuple(end_point)


def random_rectangle_vector_opted(
        vector, box, random_range=(0, 0, 0, 0), padding=15, whitelist_area=None, blacklist_area=None):
    """
    Place a vector in a box randomly.

    When emulator/game stuck, it treats a swipe as a click, clicking at the end of swipe path.
    To prevent this, random results need to be filtered.

    Args:
        vector: (x, y)
        box: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y).
        random_range (tuple): Add a random_range to vector. (x_min, y_min, x_max, y_max).
        padding (int):
        whitelist_area: (list[tuple[int]]):
            A list of area that safe to click. Swipe path will end there.
        blacklist_area: (list[tuple[int]]):
            If none of the whitelist_area satisfies current vector, blacklist_area will be used.
            Delete random path that ends in any blacklist_area.

    Returns:
        tuple(int), tuple(int): start_point, end_point.
    """
    vector = np.array(vector) + random_rectangle_point(random_range)
    vector = np.round(vector).astype(int)
    half_vector = np.round(vector / 2).astype(int)
    box_pad = np.array(box) + np.append(np.abs(half_vector) + padding, -np.abs(half_vector) - padding)
    box_pad = area_offset(box_pad, half_vector)
    segment = int(np.linalg.norm(vector) // 70) + 1

    def in_blacklist(end):
        if not blacklist_area:
            return False
        for x in range(segment + 1):
            point = - vector * x / segment + end
            for area in blacklist_area:
                if point_in_area(point, area, threshold=0):
                    return True
        return False

    if whitelist_area:
        for area in whitelist_area:
            area = area_limit(area, box_pad)
            if all([x > 0 for x in area_size(area)]):
                end_point = random_rectangle_point(area)
                for _ in range(10):
                    if in_blacklist(end_point):
                        continue
                    return point_limit(end_point - vector, box), point_limit(end_point, box)

    for _ in range(100):
        end_point = random_rectangle_point(box_pad)
        if in_blacklist(end_point):
            continue
        return point_limit(end_point - vector, box), point_limit(end_point, box)

    end_point = random_rectangle_point(box_pad)
    return point_limit(end_point - vector, box), point_limit(end_point, box)


def random_line_segments(p1, p2, n, random_range=(0, 0, 0, 0)):
    """Cut a line into multiple segments.

    Args:
        p1: (x, y).
        p2: (x, y).
        n: Number of slice.
        random_range: Add a random_range to points.

    Returns:
        list[tuple]: [(x0, y0), (x1, y1), (x2, y2)]
    """
    return [tuple((((n - index) * p1 + index * p2) / n).astype(int) + random_rectangle_point(random_range))
            for index in range(0, n + 1)]


def get_circle_points(x,y,  show_res = False, radius=6):
    """围绕圆心绘制离散点.

    Args:
        x (_type_): _description_
        y (_type_): _description_
        show_res (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    if show_res:
        import turtle
        turtle.speed(0)
    points = []
    for r in range(5, 5*(radius+1), 5):
        n = int(2 * math.pi * r / (5))
        for i in range(n):
            angle = 2 * math.pi / n * i
            px = x + r * math.cos(angle)
            py = y + r * math.sin(angle)
            if show_res:
                turtle.penup()
                turtle.goto(px, py)
                turtle.pendown()
                turtle.dot(2)
            points.append((px, py))
    return points