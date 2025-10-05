import cv2
import traceback
from whimbox.common.utils.asset_utils import *
from whimbox.common.cvars import *

class PosiTemplate(AssetBase):
    def __init__(self, name = None, posi=None, img_path=None):
        """坐标管理类

        Args:
            posi (list, optional): 可选。若有，则使用该坐标. Defaults to None.
            img_path (str, optional): 可选。若有，则使用该图片。图片应符合bbg格式. Defaults to None.
        """
        if name is None:
            super().__init__(get_name(traceback.extract_stack()[-2]))
        else:
            super().__init__(name)
        self.posi_list = []
        self.position = None
        
        if posi is None and img_path is None:
            img_path = self.get_img_path()
        self.add_posi(posi=posi, img_path=img_path)
    
    def add_posi(self, posi=None, img_path:str = None):
        """添加坐标
        
        Args:
            posi (list, optional): 可选。若有，则使用该坐标. Defaults to None.
            img_path (str, optional): 可选。若有，则使用该图片。图片应符合bbg格式. Defaults to None.
        """
        if posi != None:
            position = posi
        else:
            # self.origin_path = img_path
            image = cv2.imread(img_path)
            position = asset_get_bbox(image, black_offset=18)
        self.posi_list.append(position)
        
        if len(self.posi_list) <= 1:
            self.position = self.posi_list[0]
        else:
            self.position = self.posi_list

class Area(PosiTemplate):
    def __init__(self, name=None):
        name = get_name(traceback.extract_stack()[-2])
        super().__init__(name)
    
    def center_position(self):
        center_posi = []
        for posi in self.posi_list:
            center_x = int((posi[0] + posi[2]) / 2)
            center_y = int((posi[1] + posi[3]) / 2)
            center_posi.append([center_x, center_y])
        if len(self.posi_list) == 1:
            return center_posi[0]
        else:
            return center_posi
