from whimbox.ui.ui import *
from whimbox.ui.ui_assets import *
import cv2, numpy as np
from whimbox.interaction.interaction_core import itt

def recaputer(img_obj:ImgIcon):
    cap_imsrc = itt.capture(posi=img_obj.cap_posi)
    imsrc = np.zeros([1080,1920,3], dtype='uint8')
    imsrc[img_obj.cap_posi[1]:img_obj.cap_posi[3], img_obj.cap_posi[0]:img_obj.cap_posi[2]] = cap_imsrc
    cv2.imwrite(img_obj.origin_path, imsrc)

if __name__ == '__main__':
    recaputer(IconUIDungeonSmallMapArrow)