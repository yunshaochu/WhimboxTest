'''生成用于匹配的地图图片'''
import os
from source.map.detection.utils import *
from source.common.utils.img_utils import *
from source.map.detection.cvars import *

def gen_luma_05x_0125x_map(org_map: MapAsset):
    '''
    生成luma_05x和luma_0125x的地图图片
    '''
    image = org_map.img
    luma_image = rgb2luma(image)
    luma_05x_image = cv2.resize(luma_image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_NEAREST)
    luma_05x_path = org_map.path.replace('.png', '_luma_05x.png')
    save_image(luma_05x_image, luma_05x_path)
    luma_0125x_image = cv2.resize(luma_image, None, fx=0.125, fy=0.125, interpolation=cv2.INTER_NEAREST)
    luma_0125x_path = org_map.path.replace('.png', '_luma_0125x.png')
    save_image(luma_0125x_image, luma_0125x_path)


def gen_arrows_map(arrow: MapAsset):
    arrows = {}
    for degree in range(0, 360):
        rotated = rotate_bound(arrow.img, degree)
        rotated = crop(rotated, area=get_bbox(rotated, threshold=15))
        rotated = color_similarity_2d(rotated, color=(255,255,255))
        arrows[degree] = rotated
    return arrows

def gen_ArrowRotateMap(arrow: MapAsset, arrows_map):
    radius = DIRECTION_RADIUS
    image = np.zeros((10 * radius * 2, 9 * radius * 2), dtype=np.uint8)
    for degree in range(0, 360, 5):
        y, x = divmod(degree / 5, 8)
        rotated = arrows_map.get(degree)
        point = (radius + int(y) * radius * 2, radius + int(x) * radius * 2)
        image[point[0]:point[0] + rotated.shape[0], point[1]:point[1] + rotated.shape[1]] = rotated
    image = cv2.resize(image, None,
                        fx=DIRECTION_SEARCH_SCALE, fy=DIRECTION_SEARCH_SCALE,
                        interpolation=cv2.INTER_NEAREST)

    path = arrow.path.replace('ARROW.png', 'ArrowRotateMap.png')
    save_image(image, path)

def gen_ArrowRotateMapAll(arrow: MapAsset, arrows_map):
    radius = DIRECTION_RADIUS
    image = np.zeros((136 * radius * 2, 9 * radius * 2), dtype=np.uint8)
    for degree in range(360 * 3):
        y, x = divmod(degree, 8)
        rotated = arrows_map.get(degree % 360)
        point = (radius + int(y) * radius * 2, radius + int(x) * radius * 2)
        image[point[0]:point[0] + rotated.shape[0], point[1]:point[1] + rotated.shape[1]] = rotated
    image = cv2.resize(image, None,
                        fx=DIRECTION_SEARCH_SCALE, fy=DIRECTION_SEARCH_SCALE,
                        interpolation=cv2.INTER_NEAREST)

    path = arrow.path.replace('ARROW.png', 'ArrowRotateMapAll.png')
    save_image(image, path)


if __name__ == '__main__':
    MiralandMapOrg = MapAsset('w01_v8')
    gen_luma_05x_0125x_map(MiralandMapOrg)

    ARROW = MapAsset('ARROW')
    arrows_map = gen_arrows_map(ARROW)
    gen_ArrowRotateMap(ARROW, arrows_map)
    gen_ArrowRotateMapAll(ARROW, arrows_map)

