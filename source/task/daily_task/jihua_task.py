"""
激化素材幻境
"""

from source.task.task_template import TaskTemplate, register_step
from source.ui.ui import ui_control
from source.ui.page_assets import *
from source.interaction.interaction_core import itt
import time
from source.ui.material_icon_assets import material_icon_dict
from source.common.utils.ui_utils import *
from source.common.cvars import DEBUG_MODE

target_material_list = ["噗灵", "丝线", "闪亮泡泡"]

class JihuaTask(TaskTemplate):
    def __init__(self, target_material, cost_material):
        super().__init__("jihua_task")
        self.target_material = target_material
        self.cost_material = cost_material

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
        if self.target_material not in target_material_list:
            raise Exception(f"不支持兑换激化产物{self.target_material}")
        itt.wait_until_stable()
        if not scroll_find_click(AreaJihuaTargetSelect, self.target_material, threshold=0.85, scale=0.5):
            raise Exception(f"未找到激化产物{self.target_material}")


    @register_step("选择激化素材")
    def step5(self):
        if self.cost_material not in material_icon_dict:
            raise Exception(f"不支持使用{self.cost_material}作为消耗材料")
        material_info = material_icon_dict[self.cost_material]
        if not material_info["jihua"]:
            raise Exception(f"{self.cost_material}不能用于激化")
        
        itt.wait_until_stable()
        if not scroll_find_click(AreaJihuaCostSelect, material_info["icon"], threshold=0.7, scale=0.5):
            raise Exception(f"未找到消耗材料{self.cost_material}")


    @register_step("选择激化素材数量")
    def step6(self):
        if DEBUG_MODE:
            # debug下，就使用一个素材，为了可以多测几次
            if wait_until_appear_then_click(ButtonJihuaNumConfirm):
                return
        else:
            if wait_until_appear_then_click(ButtonJihuaNumMax):
                time.sleep(0.2)
                if wait_until_appear_then_click(ButtonJihuaNumConfirm):
                    return
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
    jihua_task = JihuaTask("闪亮泡泡", "玉簪蚂蚱")
    jihua_task.task_run()