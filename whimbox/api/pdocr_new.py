from paddleocr import PaddleOCR
from whimbox.common.logger import logger
from whimbox.common.path_lib import ASSETS_PATH
import os
import time
import cv2
import numpy as np
import threading

# 用于存放ocr容易识别错误的映射
REPLACE_DICT = {
}

class NewPaddleOCR():
    def __init__(self, inference_path: str = None):
        if inference_path is None:
            inference_path = os.path.join(ASSETS_PATH, 'PPOCRModels')
        logger.info(f"Creating PaddleOCR object: {inference_path}")
        pt = time.time()
        self.paddleOCR = PaddleOCR(
            device='gpu',
            text_detection_model_dir=os.path.join(inference_path, 'PP-OCRv5_server_det'),
            text_recognition_model_dir=os.path.join(inference_path, 'PP-OCRv5_server_rec'),
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,)
        logger.info(f"created PP-OCRv5. cost {round(time.time() - pt, 2)}")
        self._lock = threading.Lock()
    
    def analyze(self, img:np.ndarray):
        with self._lock:
            # img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            # if CV_DEBUG_MODE:
            #     cv2.imshow("ocr", img)
            #     cv2.waitKey(1000)
            res = self.paddleOCR.predict(img, text_rec_score_thresh=0.9)
            return res[0]
    
    def _replace_texts(self, text: str):
        for i in REPLACE_DICT:
            if i in text:
                text = text.replace(i, REPLACE_DICT[i])
        return text

    def get_all_texts(self, img, mode=0, per_monitor=False):
        if per_monitor:
            pt = time.time()
        res = self.analyze(img)['rec_texts']
        if per_monitor:
            logger.info(f"ocr performance: {round(time.time() - pt, 2)}")
        ret = []
        for text in res:
            if len(text) > 1:
                ret.append(text)
        if mode == 1:
            return ','.join(str(self._replace_texts(i)) for i in ret).replace(',', '')
        return [self._replace_texts(i) for i in ret]

    def detect_and_ocr(self, img, show_res=False):
        res = self.analyze(img)
        texts = res['rec_texts']
        boxes = res['rec_boxes']
        ret = {}
        for i in range(len(texts)):
            ret[texts[i]] = boxes[i]
        if show_res:
            self._show_ocr_result(img, texts, boxes)
        return ret

    def _show_ocr_result(self, img, texts, boxes):
        """独立的画框和显示逻辑"""
        # 创建一个副本用于绘制，避免修改原图
        img_with_boxes = img.copy()
        
        for i in range(len(texts)):
            # 绘制绿色边界框
            box = boxes[i]
            # box是一个包含4个点的数组，每个点有x,y坐标
            x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
            cv2.rectangle(img_with_boxes, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 绿色框，线宽为2
            
            # 可选：在框旁边显示识别出的文字
            if len(texts[i]) > 0:
                # 在第一个点位置显示文字
                cv2.putText(img_with_boxes, str(i), (x1, y1-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
        cv2.imshow("OCR Debug", img_with_boxes)
        cv2.waitKey(0)

ocr = NewPaddleOCR()

if __name__ == '__main__':
    pt = time.time()
    img = cv2.imread("D:\\workspaces\\python\\auto_test\\assets\\imgs\\Windows\\General\\common\\AreaFPickup.jpg")
    print(ocr.get_all_texts(img, per_monitor=True))
    # img = cv2.imread("D:\\workspaces\\python\\auto_test\\assets\\imgs\\Windows\\BigMap\\common\\AreaBigMapRegionSelect.jpg")
    # img = cv2.imread("D:\\workspaces\\python\\auto_test\\tools\\snapshot\\1756453092.4205182.png")
    # print(ocr.detect_and_ocr(img))

