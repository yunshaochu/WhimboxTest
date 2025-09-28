import cv2
import numpy as np
from PIL import Image
import math
from typing import Union, Tuple

from source.common.cvars import *
from source.common.utils.posi_utils import euclidean_distance_plist
from source.common.errors import FunctionModeError


def load_image(file, area=None):
    """
    Load an image like pillow and drop alpha channel.

    Args:
        file (str):
        area (tuple):

    Returns:
        np.ndarray:
    """
    image = Image.open(file)
    if area is not None:
        image = image.crop(area)
    image = np.array(image)
    channel = image.shape[2] if len(image.shape) > 2 else 1
    if channel > 3:
        image = image[:, :, :3].copy()
    return image


def save_image(image, file):
    """
    Save an image like pillow.

    Args:
        image (np.ndarray):
        file (str):
    """
    # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    # cv2.imwrite(file, image)
    Image.fromarray(image).save(file)


def crop(image, area, copy=True):
    """
    Crop image like pillow, when using opencv / numpy.
    Provides a black background if cropping outside of image.

    Args:
        image (np.ndarray):
        area:
        copy (bool):

    Returns:
        np.ndarray:
    """
    x1, y1, x2, y2 = map(int, map(round, area))
    h, w = image.shape[:2]
    border = np.maximum((0 - y1, y2 - h, 0 - x1, x2 - w), 0)
    x1, y1, x2, y2 = np.maximum((x1, y1, x2, y2), 0)
    image = image[y1:y2, x1:x2]
    if sum(border) > 0:
        image = cv2.copyMakeBorder(image, *border, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
    if copy:
        image = image.copy()
    return image


def resize(image, size):
    """
    Resize image like pillow image.resize(), but implement in opencv.
    Pillow uses PIL.Image.NEAREST by default.

    Args:
        image (np.ndarray):
        size: (x, y)

    Returns:
        np.ndarray:
    """
    return cv2.resize(image, size, interpolation=cv2.INTER_NEAREST)


def image_channel(image):
    """
    Args:
        image (np.ndarray):

    Returns:
        int: 0 for grayscale, 3 for RGB.
    """
    return image.shape[2] if len(image.shape) == 3 else 0


def image_size(image):
    """
    Args:
        image (np.ndarray):

    Returns:
        int, int: width, height
    """
    shape = image.shape
    return shape[1], shape[0]


def image_paste(image, background, origin):
    """
    Paste an image on background.
    This method does not return a value, but instead updates the array "background".

    Args:
        image:
        background:
        origin: Upper-left corner, (x, y)
    """
    x, y = origin
    w, h = image_size(image)
    background[y:y + h, x:x + w] = image


def rgb2gray(image):
    """
    Args:
        image (np.ndarray): Shape (height, width, channel)

    Returns:
        np.ndarray: Shape (height, width)
    """
    r, g, b = cv2.split(image)
    return cv2.add(
        cv2.multiply(cv2.max(cv2.max(r, g), b), 0.5),
        cv2.multiply(cv2.min(cv2.min(r, g), b), 0.5)
    )


def rgb2hsv(image):
    """
    Convert RGB color space to HSV color space.
    HSV is Hue Saturation Value.

    Args:
        image (np.ndarray): Shape (height, width, channel)

    Returns:
        np.ndarray: Hue (0~360), Saturation (0~100), Value (0~100).
    """
    image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV).astype(float)
    image *= (360 / 180, 100 / 255, 100 / 255)
    return image


def rgb2yuv(image):
    """
    Convert RGB to YUV color space.

    Args:
        image (np.ndarray): Shape (height, width, channel)

    Returns:
        np.ndarray: Shape (height, width)
    """
    image = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
    return image


def rgb2luma(image):
    """
    Convert RGB to the Y channel (Luminance) in YUV color space.

    Args:
        image (np.ndarray): Shape (height, width, channel)

    Returns:
        np.ndarray: Shape (height, width)
    """
    image = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
    luma, _, _ = cv2.split(image)
    return luma


def get_color(image, area):
    """Calculate the average color of a particular area of the image.

    Args:
        image (np.ndarray): Screenshot.
        area (tuple): (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y)

    Returns:
        tuple: (r, g, b)
    """
    temp = crop(image, area, copy=False)
    color = cv2.mean(temp)
    return color[:3]


def get_bbox(image, threshold=0):
    """
    A numpy implementation of the getbbox() in pillow.

    Args:
        image (np.ndarray): Screenshot.
        threshold (int): Color <= threshold will be considered black

    Returns:
        tuple: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y)
    """
    if image_channel(image) == 3:
        image = np.max(image, axis=2)
    x = np.where(np.max(image, axis=0) > threshold)[0]
    y = np.where(np.max(image, axis=1) > threshold)[0]
    return x[0], y[0], x[-1] + 1, y[-1] + 1


def get_bbox_reversed(image, threshold=0):
    """
    Similar to `get_bbox` but for black contents on white background.

    Args:
        image (np.ndarray): Screenshot.
        threshold (int): Color >= threshold will be considered white

    Returns:
        tuple: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y)
    """
    if image_channel(image) == 3:
        image = np.min(image, axis=2)
    x = np.where(np.min(image, axis=0) < threshold)[0]
    y = np.where(np.min(image, axis=1) < threshold)[0]
    return x[0], y[0], x[-1] + 1, y[-1] + 1


def color_similarity(color1, color2):
    """
    Args:
        color1 (tuple): (r, g, b)
        color2 (tuple): (r, g, b)

    Returns:
        int:
    """
    diff = np.array(color1).astype(int) - np.array(color2).astype(int)
    diff = np.max(np.maximum(diff, 0)) - np.min(np.minimum(diff, 0))
    return diff


def color_similar(color1, color2, threshold=10):
    """Consider two colors are similar, if tolerance lesser or equal threshold.
    Tolerance = Max(Positive(difference_rgb)) + Max(- Negative(difference_rgb))
    The same as the tolerance in Photoshop.

    Args:
        color1 (tuple): (r, g, b)
        color2 (tuple): (r, g, b)
        threshold (int): Default to 10.

    Returns:
        bool: True if two colors are similar.
    """
    # print(color1, color2)
    diff = np.array(color1).astype(int) - np.array(color2).astype(int)
    diff = np.max(np.maximum(diff, 0)) - np.min(np.minimum(diff, 0))
    return diff <= threshold


def color_similar_1d(image, color, threshold=10):
    """
    Args:
        image (np.ndarray): 1D array.
        color: (r, g, b)
        threshold(int): Default to 10.

    Returns:
        np.ndarray: bool
    """
    diff = image.astype(int) - color
    diff = np.max(np.maximum(diff, 0), axis=1) - np.min(np.minimum(diff, 0), axis=1)
    return diff <= threshold


def color_similarity_2d(image, color):
    """
    Args:
        image: 2D array.
        color: (r, g, b)

    Returns:
        np.ndarray: uint8
    """
    r, g, b = cv2.split(cv2.subtract(image, (*color, 0)))
    positive = cv2.max(cv2.max(r, g), b)
    r, g, b = cv2.split(cv2.subtract((*color, 0), image))
    negative = cv2.max(cv2.max(r, g), b)
    return cv2.subtract(255, cv2.add(positive, negative))


def color_mapping(image, max_multiply=2):
    """
    Mapping color to 0-255.
    Minimum color to 0, maximum color to 255, multiply colors by 2 at max.

    Args:
        image (np.ndarray):
        max_multiply (int, float):

    Returns:
        np.ndarray:
    """
    image = image.astype(float)
    low, high = np.min(image), np.max(image)
    multiply = min(255 / (high - low), max_multiply)
    add = (255 - multiply * (low + high)) / 2
    image = cv2.add(cv2.multiply(image, multiply), add)
    image[image > 255] = 255
    image[image < 0] = 0
    return image.astype(np.uint8)


def similar_img(img, target, is_gray=False, is_show_res: bool = False, ret_mode=IMG_RATE) -> Union[float, Tuple[float,float]]:
    """单个图片匹配

    Args:
        img (numpy): Mat
        template (numpy): 要匹配的样板图片
        is_gray (bool, optional): 是否启用灰度匹配. Defaults to False.
        is_show_res (bool, optional): 结果显示. Defaults to False.
        ret_mode (int, optional): 返回值模式. Defaults to IMG_RATE.

    Returns:
        float/(float, list[]): 匹配度或者匹配度和它的坐标
    """
    if is_gray:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        target = cv2.cvtColor(target, cv2.COLOR_BGRA2GRAY)
    # 模板匹配，将alpha作为mask，TM_CCORR_NORMED方法的计算结果范围为[0, 1]，越接近1越匹配
    # img_manager.qshow(img)
    result = cv2.matchTemplate(img, target, cv2.TM_CCORR_NORMED)  # TM_CCOEFF_NORMED
    # 获取结果中最大值和最小值以及他们的坐标
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if is_show_res:
        cv2.waitKey(0)
    # 在窗口截图中匹配位置画红色方框
    matching_rate = max_val
    
    if ret_mode == IMG_RATE:
        return matching_rate
    elif ret_mode == IMG_RECT:
        return matching_rate, max_loc
    else:
        raise FunctionModeError


def match_multiple_img(img, template, is_gray=False, is_show_res: bool = False, ret_mode=IMG_POINT,
                           threshold=0.98, ignore_close=False):
    """多图片识别

    Args:
        img (numpy): 截图Mat
        template (numpy): 要匹配的样板图片
        is_gray (bool, optional): 是否启用灰度匹配. Defaults to False.
        is_show_res (bool, optional): 结果显示. Defaults to False.
        ret_mode (int, optional): 返回值模式,目前只有IMG_POINT. Defaults to IMG_POINT. 
        threshold (float, optional): 最小匹配度. Defaults to 0.98.

    Returns:
        list[list[], ...]: 匹配成功的坐标列表
    """
    if is_gray:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        template = cv2.cvtColor(template, cv2.COLOR_BGRA2GRAY)
    res_posi = []
    res = cv2.matchTemplate(img, template, cv2.TM_CCORR_NORMED)
    # res = cv2.matchTemplate(img, template, cv2.TM_CCORR_NORMED)  # TM_CCOEFF_NORMED
    # img_manager.qshow(template)
    # h, w = template.shape[:2]  # 获取模板高和宽
    loc = np.where(res >= threshold)  # 匹配结果小于阈值的位置
    
    # Sort coordinates of matched pixels by their similarity score in descending order
    matched_coordinates = sorted(zip(*loc[::-1]), key=lambda x: res[x[1], x[0]], reverse=True)
    if ignore_close:
        ret_coordinates = []
        for i in matched_coordinates:
            if len(ret_coordinates) == 0:
                ret_coordinates.append(i)
                continue
            if min(euclidean_distance_plist(i, ret_coordinates))>=15:
                ret_coordinates.append(i)
        return ret_coordinates
    # for pt in zip(*loc[::-1]):  # 遍历位置，zip把两个列表依次参数打包
    #     right_bottom = (pt[0] + w, pt[1] + h)  # 右下角位置
    #     if ret_mode == IMG_RECT:
    #         res_posi.append([pt[0], pt[1], pt[0] + w, pt[1] + h])
    #     else:
    #         res_posi.append([pt[0] + w / 2, pt[1] + h / 2])
    #     # cv2.rectangle((show_img), pt, right_bottom, (0,0,255), 2) #绘制匹配到的矩阵
    # if is_show_res:
    #     show_img = img.copy()
    #     # print(*loc[::-1])
    #     for pt in zip(*loc[::-1]):  # 遍历位置，zip把两个列表依次参数打包
    #         right_bottom = (pt[0] + w, pt[1] + h)  # 右下角位置
    #         cv2.rectangle((show_img), pt, right_bottom, (0, 0, 255), 2)  # 绘制匹配到的矩阵
    #     cv2.imshow("img", show_img)
    #     cv2.imshow("template", template)
    #     cv2.waitKey(0)  # 获取按键的ASCII码
    #     cv2.destroyAllWindows()  # 释放所有的窗口

    return matched_coordinates


def png2jpg(png, bgcolor='black', channel='bg', alpha_num=50):
    """将4通道png转换为3通道jpg

    Args:
        png (Mat/ndarray): 4通道图片
        bgcolor (str, optional): 背景的颜色. Defaults to 'black'.
        channel (str, optional): 提取背景或UI. Defaults to 'bg'.
        alpha_num (int, optional): 透明通道的大小. Defaults to 50.

    Returns:
        Mat/ndarray: 3通道图片
    """
    if bgcolor == 'black':
        bgcol = 0
    else:
        bgcol = 255

    jpg = png[:, :, :3]
    if channel == 'bg':
        over_item_list = png[:, :, 3] > alpha_num
    else:
        over_item_list = png[:, :, 3] < alpha_num
    jpg[:, :, 0][over_item_list] = bgcol
    jpg[:, :, 1][over_item_list] = bgcol
    jpg[:, :, 2][over_item_list] = bgcol
    return jpg

def add_padding(image, padding):
    return cv2.copyMakeBorder(image, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=(0, 0, 0))

def process_with_hsv_limit(image, lower_limit, upper_limit):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv, lower_limit, upper_limit)