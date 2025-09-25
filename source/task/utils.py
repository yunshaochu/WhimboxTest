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
