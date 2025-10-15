'''简简单单的截图工具'''

import cv2
import time
from whimbox.interaction.interaction_core import itt
from whimbox.common.path_lib import *
os.startfile(ROOT_PATH + '\\' + "..\\tools\\snapshot")
while 1:
    input('enter to capture') 
    # time.sleep(0.2)
    cap = itt.capture()
    cv2.imwrite(ROOT_PATH + '\\' + "..\\tools\\snapshot\\" + str(time.time()) + ".png", cap) # type: ignore