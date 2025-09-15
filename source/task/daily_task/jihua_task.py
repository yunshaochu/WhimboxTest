"""
激化素材幻境
"""

from source.task.task_template import TaskTemplate, register_step
from source.ui.ui import ui_control
from source.ui.page_assets import *
from source.interaction.interaction_core import itt
import time
from source.task.utils import *


class JihuaTask(TaskTemplate):
    def __init__(self):
        super().__init__("jihua_task")


    @register_step("正在前往素材激化幻境")
    def step1(self):
        ui_control.ui_goto(page_jihua)


    @register_step("继续前往素材激化幻境")
    def step2(self):
        if not wait_until_appear_then_click(ButtonJihuaInnerGo):
            raise Exception("未找到素材激化幻境入口")


    @register_step("正在前往激化台")
    def step3(self):
        if not wait_until_appear(IconUIMeiyali, retry_time=10):
            raise Exception("未进入素材激化幻境")
        
        retry_time = 3
        while retry_time > 0:
            itt.key_down('w')
            time.sleep(0.8)
            itt.key_up('w')
            time.sleep(0.2) # 等待弹出按钮
            if itt.get_text_existence(TextJihuatai):
                itt.key_press('f')
                return
            retry_time -= 1
        else:
            raise Exception("未找到素材激化台")


    @register_step("选择兑换产物")
    def step4(self):
        if not wait_until_appear_then_click(ButtonJihuaPaopao):
            raise Exception("未进入兑换产物界面")


    @register_step("选择激化素材")
    def step5(self):
        if not wait_until_appear(IconUIJihuaSelect):
            raise Exception("未进入激化素材选择界面")
        
        for _ in range(5):
            pos, _ = find_game_img_in_area(T_Icon_item_AN0080, AreaUIJihuaSelect, scale=0.5)
            if pos:
                target_x = (pos[0] + pos[2]) // 2
                target_y = (pos[1] + pos[3]) // 2
                itt.move_and_click([target_x, target_y])
                break
            else:    
                itt.move_to([1028, 150]) # 滚动条位置
                itt.middle_scroll(-15)
                time.sleep(0.2) # 等待滚动完成
        else:
            raise Exception("未找到合适的激化素材")

    @register_step("选择激化素材数量")
    def step6(self):
        if wait_until_appear_then_click(ButtonJihuaNumMax):
            time.sleep(0.2)
            if wait_until_appear_then_click(ButtonJihuaNumConfirm):
                return
        # if wait_until_appear_then_click(ButtonJihuaNumConfirm):
        #     return
        raise Exception("未弹出素材数量选择框")

    @register_step("确认开始激化")
    def step7(self):
        if not wait_until_appear_then_click(ButtonJihuaFinallyConfirm):
            raise Exception("确认激化按钮不见了")
        
    @register_step("等待激化完成")
    def step8(self):
        if wait_until_appear(TextFSkip):
            itt.key_press('f')
            time.sleep(0.2)
            if wait_until_appear(TextClickSkip):
                itt.key_press('f')
                time.sleep(0.2)
                itt.key_press('esc')
                self.update_task_result(message="激化完成")
                return
        raise Exception("卡在激化完成的时候了？！")

    @register_step("退出激化幻境")
    def step9(self):
        if wait_until_appear(IconUIMeiyali):
            itt.key_press('backspace')
            return
        raise Exception("退不出激化幻境了？！")



if __name__ == "__main__":
    jihua_task = JihuaTask()
    jihua_task.task_run()



