'''领取大月卡奖励'''
from whimbox.task.task_template import TaskTemplate, register_step
from whimbox.ui.ui import ui_control
from whimbox.ui.page_assets import *
import time
from whimbox.common.utils.ui_utils import *

class MonthlyPassTask(TaskTemplate):
    def __init__(self):
        super().__init__("monthly_pass_task")

    @register_step("打开奇迹之旅")
    def step1(self):
        ui_control.ui_goto(page_monthly_pass)
    
    @register_step("领取奖励")
    def step2(self):
        if wait_until_appear_then_click(ButtonMonthlyPassTab2):
            wait_until_appear_then_click(ButtonMonthlyPassAward)
            time.sleep(0.5)
            if wait_until_appear_then_click(ButtonMonthlyPassTab1):
                if wait_until_appear_then_click(ButtonMonthlyPassAward):
                    if wait_until_appear(TextClickSkip):
                        itt.key_press('f')
                        time.sleep(0.2)
                        self.update_task_result(message="成功领取奇迹之旅奖励")
                    return
        self.update_task_result(message="奇迹之旅无奖励可领取")
        
    @register_step("退出奇迹之旅")
    def step3(self):
        ui_control.ui_goto(page_main)

if __name__ == "__main__":
    task = MonthlyPassTask()
    result = task.task_run()
    print(result.to_dict())