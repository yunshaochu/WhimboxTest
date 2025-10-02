from rapidocr import RapidOCR
import os
import threading
import time
import cv2
import numpy as np
from source.common.utils.img_utils import similar_img
from source.common.logger import logger
from source.common.path_lib import CONFIG_PATH

# 错误替换表
REPLACE_DICT = {}

class RapidOcr():
    def __init__(self):
        logger.info(f"Creating RapidOCR object")
        pt = time.time()
        config_path = os.path.join(CONFIG_PATH, 'rapidocr.yaml')
        self.ocr = RapidOCR(config_path=config_path)
        logger.info(f"created RapidOCR. cost {round(time.time() - pt, 2)}")
        self._lock = threading.Lock()
        # self.last_img: np.ndarray = None
        # self.last_result = None

    def _replace_texts(self, text: str):
        for i in REPLACE_DICT:
            if i in text:
                text = text.replace(i, REPLACE_DICT[i])
        return text

    def analyze(self, img):
        """直接调用 RapidOCR 的接口"""
        with self._lock:
            # # 如果上一次ocr的图片和这次的图片完全相同，则直接返回上一次的ocr结果
            # if self.last_img is not None:
            #     if self.last_img.shape == img.shape:
            #         similar = similar_img(self.last_img, img, is_gray=True)
            #         if similar > 0.99:
            #             logger.debug(f"ocr_rapid: similar: {similar}, return last result")
            #             return self.last_result
            result = self.ocr(img)
            # self.last_img = img
            # self.last_result = result
            return result

    def get_all_texts(self, img, mode=0, per_monitor=False):
        if per_monitor:
            pt = time.time()
        res = self.analyze(img)  # res is a RapidOCROutput object

        rec_texts = []
        if res and hasattr(res, 'txts') and res.txts:
            rec_texts = [self._replace_texts(txt) for txt in res.txts if len(txt) > 1]

        if per_monitor:
            logger.info(f"ocr performance: {round(time.time() - pt, 2)}")

        if mode == 1:
            return ''.join(rec_texts)
        return rec_texts

    def _show_ocr_result(self, img, res):
        """独立的画框和显示逻辑"""
        # 创建一个副本用于绘制，避免修改原图
        img_with_boxes = img.copy()
        
        for box in res.values():
            # 绘制绿色边界框
            x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
            cv2.rectangle(img_with_boxes, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 绿色框，线宽为2
            
        cv2.imshow("OCR Debug", img_with_boxes)
        cv2.waitKey(0)

    def detect_and_ocr(self, img, show_res=False):
        res = self.analyze(img)
        ret = {}
        if res and res.boxes is not None and res.txts is not None:
            for box, txt in zip(res.boxes, res.txts):
                if len(txt) > 1:
                    # 简化为左上角和右下角坐标，方便后续点击
                    x_coords = [point[0] for point in box]
                    y_coords = [point[1] for point in box]
                    left_top_x = min(x_coords)
                    left_top_y = min(y_coords)
                    right_bottom_x = max(x_coords)
                    right_bottom_y = max(y_coords)
                    simplified_box = [left_top_x, left_top_y, right_bottom_x, right_bottom_y]
                    # todo: 可能识别出多个相同的文本，需要优化
                    ret[self._replace_texts(txt)] = simplified_box

        if show_res:
            self._show_ocr_result(img, ret)
        return ret

ocr = RapidOcr()

# ---------------- 调用 Demo ----------------
if __name__ == '__main__':
    from source.common.path_lib import ASSETS_PATH
    from source.common.utils.img_utils import add_padding
    path = os.path.join(ASSETS_PATH, "imgs", "Windows", "BigMap", "common", "111.png")
    img = cv2.imread(path)
    img = add_padding(img, 50)
    print(ocr.get_all_texts(img, mode=1, per_monitor=True))
    # path = os.path.join(ASSETS_PATH, "imgs", "Windows", "BigMap", "common", "AreaBigMapRegionSelect.jpg")
    # img = cv2.imread(path)
    # print(ocr.detect_and_ocr(img, show_res=True))
