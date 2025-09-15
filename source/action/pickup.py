from source.task.task_template import TaskTemplate, register_step
from source.interaction.interaction_core import itt
from source.api.pdocr_new import ocr
from source.ui.ui_assets import TextFPickUp
from source.common.cvars import DEBUG_MODE

class PickupTask(TaskTemplate):
    def __init__(self):
        super().__init__("pickup_task")

    @register_step("开始采集")
    def step1(self):
        pickup_item_dict = {}
        while True:
            cap = itt.capture(posi=TextFPickUp.cap_area)
            texts = ocr.get_all_texts(cap)
            if len(texts) == 2 and texts[1] == TextFPickUp.text:
                pickup_item = texts[0]
                if pickup_item in pickup_item_dict:
                    pickup_item_dict[pickup_item] += 1
                else:
                    pickup_item_dict[pickup_item] = 1
                if DEBUG_MODE:
                    # debug模式下，不采集，这样可以多测几遍
                    itt.delay(0.2, comment="等待采集完成")
                    break
                else:
                    itt.key_press('f')
                    itt.delay(0.2, comment="等待采集完成")
            else:
                break
        
        if len(pickup_item_dict) == 0:
            self.update_task_result(message="未采集到物品")
            self.log_to_gui("未采集到物品")
            return
        res = ''
        for key, value in pickup_item_dict.items():
            res += f"{key}x{value},"
        self.update_task_result(message=res)
        self.log_to_gui(f"已采集:{res}")

if __name__ == "__main__":
    import time
    import cv2
    while True:
        cap = itt.capture(posi=TextFPickUp.cap_area)
        texts = ocr.get_all_texts(cap)
        if len(texts) != 2:
            print(texts)
            cv2.imshow("cap", cap)
            cv2.waitKey(0)
        time.sleep(0.2)