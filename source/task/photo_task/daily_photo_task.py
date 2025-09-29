from source.task.task_template import TaskTemplate, register_step
from source.ui.ui import ui_control
from source.ui.page_assets import *
from source.interaction.interaction_core import itt
from source.common.utils.ui_utils import wait_until_appear, wait_until_appear_then_click

class DailyPhotoTask(TaskTemplate):
    def __init__(self):
        super().__init__("daily_photo_task")

    @register_step("前往拍照界面")
    def step1(self):
        ui_control.ui_goto(page_photo)
    
    @register_step("开始拍照")
    def step2(self):
        itt.key_press('space')

    @register_step("删除任务照片")
    def step3(self):
        if wait_until_appear(IconPhotoEdit):
            self.update_task_result(message="每日任务拍照完成")
            itt.move_and_click(IconPhotoDelete.cap_center_position_xy)
            if wait_until_appear_then_click(ButtonPhotoDeleteConfirm):
                return
        else:
            raise Exception("拍照未成功")

    @register_step("退出拍照")
    def step4(self):
        ui_control.ui_goto(page_main)

if __name__ == "__main__":
    daily_photo_task = DailyPhotoTask()
    daily_photo_task.task_run()
    print(daily_photo_task.task_result)