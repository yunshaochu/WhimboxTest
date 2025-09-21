from rapidocr import RapidOCR
import os
import threading
import time
import cv2
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

    def _replace_texts(self, text: str):
        for i in REPLACE_DICT:
            if i in text:
                text = text.replace(i, REPLACE_DICT[i])
        return text

    def analyze(self, img):
        """直接调用 RapidOCR 的接口"""
        with self._lock:
            result = self.ocr(img)
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

    def _show_ocr_result(self, img, result):
        """独立的画框和显示逻辑"""
        img_with_boxes = img.copy()
        if result and result.boxes is not None and result.txts is not None:
            for box, txt in zip(result.boxes, result.txts):
                pts = box.astype(int).reshape((-1, 1, 2))
                cv2.polylines(img_with_boxes, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
                
                y_pos = int(box[0][1]) - 10
                if y_pos < 10: y_pos = int(box[0][1]) + 20
                cv2.putText(img_with_boxes, txt, (int(box[0][0]), y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.imshow("OCR Debug", img_with_boxes)
        cv2.waitKey(0)
        cv2.destroyWindow("OCR Debug")

    def detect_and_ocr(self, img, show_res=False):
        res = self.analyze(img)
        ret = {}
        if res and res.boxes is not None and res.txts is not None:
            for box, txt in zip(res.boxes, res.txts):
                if len(txt) > 1:
                    ret[self._replace_texts(txt)] = box

        if show_res:
            self._show_ocr_result(img, res)
        return ret

ocr = RapidOcr()

# ---------------- 调用 Demo ----------------
if __name__ == '__main__':
    from source.common.path_lib import ASSETS_PATH
    
    img_path = os.path.join(ASSETS_PATH, "1.jpg")
    img = cv2.imread(img_path)

    if img is None:
        logger.error(f"Error: Could not read image from {img_path}")
    else:
        logger.info("--- Testing get_all_texts ---")
        texts = ocr.get_all_texts(img, per_monitor=True)
        logger.info(texts)

        logger.info("\n--- Testing get_all_texts (mode=1) ---")
        text_str = ocr.get_all_texts(img, mode=1)
        logger.info(text_str)

        logger.info("\n--- Testing detect_and_ocr ---")
        text_box_map = ocr.detect_and_ocr(img)
        logger.info(text_box_map)

        logger.info("\n--- Testing detect_and_ocr with show_res=True ---")
        logger.info("A window with the image and OCR results should appear.")
        try:
            ocr.detect_and_ocr(img, show_res=True)
            logger.info("Test finished. Close the image window to continue.")
        except Exception as e:
            logger.error(f"An error occurred during visualization: {e}", exc_info=True)
            logger.warning("This might be because you are running in an environment without a GUI.")
