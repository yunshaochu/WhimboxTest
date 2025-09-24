"""
美鸭梨挖掘
"""

from source.task.task_template import TaskTemplate, register_step
from source.ui.ui import ui_control
from source.ui.page_assets import *
from source.interaction.interaction_core import itt
import time
from source.task.utils import *

dig_item_dict ={
    "插梳鱼": {
        "game_img": T_Icon_item_AN0080,
        "type_button": ButtonDigType1,
        "sub_type_button": ButtonDigType1Fish,
    },
    "玉簪蚂蚱": {
        "game_img": T_Icon_item_AN0068R2,
        "type_button": ButtonDigType1,
        "sub_type_button": ButtonDigType1Insect,
    },
    "纯真丝线": {
        "game_img": T_UI_icon_004,
        "type_button": ButtonDigType2,
    },
    "闪光粒子": {
        "game_img": T_UI_icon_006,
        "type_button": ButtonDigType2,
    },
}

class DigTask(TaskTemplate):
    def __init__(self, target_item_list=["玉簪蚂蚱", "闪光粒子", "纯真丝线", "插梳鱼"]):
        super().__init__("dig_task")
        self.target_item_list = target_item_list
    
    @register_step("正在前往美鸭梨挖掘")
    def step1(self):
        ui_control.ui_goto(page_dig)


    @register_step("判断是否可收获")
    def step2(self):
        if wait_until_appear_then_click(ButtonDigGather):
            return "step3" # 可一键收获，执行收获流程
        else:
            dig_num_str = itt.ocr_single_line(AreaTextDigingNum, padding=30)
            try:
                diging_num = int(dig_num_str.split("/")[0])
            except:
                raise Exception(f"挖掘数量识别异常:{dig_num_str}")
            if diging_num > 0:
                self.log_to_gui(f"当前正在挖掘{dig_num_str}")
                self.update_task_result(message=f"已在挖掘，不进行任何操作")
                return "step5" # 有东西正在挖掘，退出
            else:
                return "step4" # 没东西在挖掘，进入挖掘步骤


    @register_step("确认挖掘产出")
    def step3(self):
        if wait_until_appear_then_click(ButtonDigGatherConfirm):
            return
        raise Exception("未弹出挖掘产出窗口")


    @register_step("选择挖掘产物")
    def step4(self):

        def select_dig_item(item_name):
            if item_name not in dig_item_dict:
                raise Exception(f"暂不支持挖掘{item_name}")
            item_info = dig_item_dict[item_name]
            # 选择物品大分类
            type_button = item_info["type_button"]
            itt.move_and_click(type_button.click_position())
            time.sleep(0.5)
            # 选择物品小分类
            if "sub_type_button" in item_info:
                sub_type_button = item_info["sub_type_button"]
                itt.move_and_click(sub_type_button.click_position())
                time.sleep(0.5)
            # 寻找物品图标
            pos, _ = find_game_img_in_area(item_info["game_img"], AreaUIDigItemSelect, scale=0.46)
            if pos is None:
                raise Exception(f"未找到{item_name}，请检查是否在挖掘界面")
            target_x = (pos[0] + pos[2]) // 2
            target_y = (pos[1] + pos[3]) // 2
            itt.move_and_click([target_x, target_y])
            time.sleep(0.5)
            # 选择挖掘时间
            if wait_until_appear(ButtonDigConfirm):
                if wait_until_appear_then_click(ButtonDigTime20h):
                    time.sleep(0.2)
                    itt.move_and_click(ButtonDigConfirm.click_position())
                    time.sleep(0.2)
                    self.log_to_gui(f"确认挖掘：{item_name}")
                    return
            raise Exception("未找到挖掘确认按钮")

        for item_name in self.target_item_list:
            select_dig_item(item_name)
            time.sleep(0.5)
        
        self.update_task_result(message=f"已开始挖掘{",".join(self.target_item_list)}")

    @register_step("退出美鸭梨挖掘")
    def step5(self):
        ui_control.ui_goto(page_main)

if __name__ == "__main__":
    dig_task = DigTask()
    dig_task.task_run()