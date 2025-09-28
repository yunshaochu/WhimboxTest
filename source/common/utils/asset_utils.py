import os
import numpy as np

from source.common.errors import *
from source.common.logger import logger
from source.common.utils.utils import load_json
from source.common.path_lib import ASSETS_PATH
from source.common.cvars import *
from source.common.utils.img_utils import image_channel

ASSETS_INDEX_JSON = load_json("imgs_index.json", fr"{ASSETS_PATH}/imgs")

def get_name(x):
    (filename, line_number, function_name, text) = x
    # = traceback.extract_stack()[-2]
    return text[:text.find('=')].strip()


def asset_get_bbox(image, black_offset=15):
    """
    A numpy implementation of the getbbox() in pillow.完全低于阈值返回None
    Args:
        image (np.ndarray): Screenshot.
    Returns:
        tuple: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y)
    """
    if image_channel(image) == 3:
        image = np.max(image, axis=2)
    x = np.where(np.max(image, axis=0) > black_offset)[0]
    y = np.where(np.max(image, axis=1) > black_offset)[0]
    if x.size == 0 or y.size == 0:
        return None
    return (x[0], y[0], x[-1] + 1, y[-1] + 1)


class AssetBase():
    def __init__(self, name: str, print_log:int=LOG_NONE) -> None:
        if name is None:
            raise NAME_NOT_FOUND
        self.name = name
        self.print_log = print_log

    def get_img_path(self):
        if self.name in ASSETS_INDEX_JSON:
            if 'common' in ASSETS_INDEX_JSON[self.name]:
                return ASSETS_INDEX_JSON[self.name]['common']
            # elif GLOBAL_LANG in ASSETS_INDEX_JSON[self.name]:
                # return ASSETS_INDEX_JSON[self.name][GLOBAL_LANG]
        r = self.search_path(self.name)
        if r != None:
            return r
        else:
            raise IMG_NOT_FOUND(self.name)

    def search_path(self, filename) -> str:
        for comp_filename in [filename + '.png', filename + '.jpg']:
            folder_path = os.path.join(ASSETS_PATH)
            for root, dirs, files in os.walk(folder_path):
                if comp_filename in files:
                    return os.path.abspath(os.path.join(root, comp_filename))

    def is_print_log(self, b: bool):
        if b:
            if self.print_log == LOG_WHEN_TRUE or self.print_log == LOG_ALL:
                return True
            else:
                return False
        else:
            if self.print_log == LOG_WHEN_FALSE or self.print_log == LOG_ALL:
                return True
            else:
                return False