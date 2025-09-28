from source.common.timer_module import AdvanceTimer
from source.task.task_template import TaskTemplate, register_step
from source.interaction.interaction_core import itt
from source.ability.ability import ability_manager
from source.ability.cvar import *
from source.map.track import *
from source.view_and_move.utils import *
from source.view_and_move.view import *
from source.view_and_move.cvars import *
from source.common.utils.ui_utils import *

class MaterialTrackBaseTask(TaskTemplate):
    def __init__(self, material_name, expected_count=1, check_stop_func=None):
        super().__init__("MaterialTrackBaseTask", check_stop_func)
        self.material_name = material_name
        if material_name not in material_icon_dict:
            raise Exception(f"不支持追踪{material_name}")
        material_info = material_icon_dict[material_name]
        if not material_info["track"]:
            raise Exception(f"不支持追踪{material_name}")
        self.ability_name = material_type_to_ability_name[material_info["type"]]
        self.time_limit = 15 # 一次任务的时间限制，超时就强制结束，单位秒
        self.material_count_dict = {self.material_name: 0}
        self.expected_count = expected_count

    def pre_play_func(self):
        # 交互动作前摇，不同类别的材料，交互方式不一样，需要单独实现
        pass

    def post_play_func(self):
        # 交互动作后摇，不同类别的材料，交互方式不一样，需要单独实现
        pass

    @register_step("切换能力")
    def step1(self):
        ability_manager.change_ability(self.ability_name)

    @register_step("开启材料追踪")
    def step2(self):
        material_track.change_tracking_material(self.material_name)

    @register_step("开始前往采集")
    def step3(self):
        ability_active_times = 0
        material_track_failed_times = 0
        timer = AdvanceTimer(self.time_limit)
        timer.start()
        while not timer.reached() and not self.need_stop() \
        and self.material_count_dict[self.material_name] < self.expected_count:
            no_material_near = False
            itt.right_down()
            itt.key_down('w')
            while not timer.reached() and not self.need_stop():
                if not material_track.is_ability_active():
                    ability_active_times = 0
                    degree = material_track.get_material_track_degree()
                    if degree is None:
                        # 容易出现短暂识别失败的情况，所以需要连续几次失败，才认为附近真的没有材料了
                        material_track_failed_times += 1
                        if material_track_failed_times > 5:
                            no_material_near = True
                            break
                        else:
                            continue
                    else:
                        material_track_failed_times = 0
                    change_view_to_angle(degree, offset=3, use_last_rotation = True)
                else:
                    # 当能力按钮连续亮起3次后，才开始采集
                    if ability_active_times < 3:
                        ability_active_times += 1
                    else:
                        itt.right_up()
                        itt.key_up('w')
                        self.pre_play_func()
                        time.sleep(0.8) # 等待采集结果文字出现
                        text = itt.ocr_single_line(AreaMaterialGetText)
                        print(text)
                        if self.material_name in text:
                            self.log_to_gui(f"{self.material_name} x 1")
                            self.material_count_dict[self.material_name] += 1
                        self.post_play_func()
                        break
            if no_material_near:
                break
        itt.right_up()
        itt.key_up('w')
        self.update_task_result(
            message=f"获得{self.material_name}x{self.material_count_dict[self.material_name]}",
            data=self.material_count_dict
        )