"""
美鸭梨挖掘
"""

from source.task.task_template import TaskTemplate, register_step
from source.ui.ui import ui_control
from source.ui.page_assets import *
from source.interaction.interaction_core import itt
import time
from source.ui.material_icon_assets import material_icon_dict
from source.common.utils.ui_utils import *

material_type_dict = {
    'plant': {
        "main_type_icon": IconMaterialTypeDig1,
        "sub_type_icon": IconMaterialTypePlant,
    },
    'animal': {
        "main_type_icon": IconMaterialTypeDig1,
        "sub_type_icon": IconMaterialTypeAnimal,
    },
    'insect': {
        "main_type_icon": IconMaterialTypeDig1,
        "sub_type_icon": IconMaterialTypeInsect,
    },
    'fish': {
        "main_type_icon": IconMaterialTypeDig1,
        "sub_type_icon": IconMaterialTypeFish,
    },
    'other': {
        "main_type_icon": IconMaterialTypeOther,
    },
    'monster': {
        "main_type_icon": IconMaterialTypeMonster,
    },
}

class DigTask(TaskTemplate):
    def __init__(self, target_item_list=["云尾锦鲤", "玉簪蚱蜢", "画眉毛团", "纯真丝线"]):
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
            dig_num_str = itt.ocr_single_line(AreaDigingNumText, padding=50)
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
            if item_name not in material_icon_dict:
                raise Exception(f"暂不支持挖掘{item_name}")
            material_info = material_icon_dict[item_name]
            if not material_info['dig']:
                raise Exception(f"暂不支持挖掘{item_name}")
            material_type = material_info['type']
            if material_type not in material_type_dict:
                raise Exception(f"暂不支持挖掘{material_type}类型的材料")

            hsv_limit = [np.array([0, 0, 100]), np.array([180, 60, 255])]

             # 选择物品大分类
            main_type_icon = material_type_dict[material_type]['main_type_icon']
            scroll_find_click(AreaDigMainTypeSelect, main_type_icon, threshold=0.85, hsv_limit=hsv_limit, scale=1.233)
            time.sleep(0.5)
            # 选择物品小分类
            if "sub_type_icon" in material_type_dict[material_type]:
                sub_type_icon = material_type_dict[material_type]['sub_type_icon']
                scroll_find_click(AreaDigSubTypeSelect, sub_type_icon, threshold=0.85, hsv_limit=hsv_limit, scale=0.83)
                time.sleep(0.5)

            # 寻找材料图标
            if not scroll_find_click(AreaDigItemSelect, material_info["icon"], threshold=0.7, scale=0.46):
                raise Exception(f"未找到{item_name}")
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