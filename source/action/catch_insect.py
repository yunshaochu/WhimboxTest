from source.common.timer_module import AdvanceTimer
from source.task.task_template import TaskTemplate, register_step
from source.interaction.interaction_core import itt
from source.ability.ability import ability_manager
from source.ability.cvar import *
from source.map.track import material_track
from source.map.map import nikki_map
from source.view_and_move.utils import *
from source.view_and_move.view import *

class CatchInsectTask(TaskTemplate):
    def __init__(self, insect_name, expected_count=1, check_stop_func=None):
        super().__init__("catch_insect_task", check_stop_func)
        self.insect_name = insect_name
        self.time_limit = 30 # 一次捕虫任务的时间限制，超时就强制结束，单位秒
        self.material_count_dict = {self.insect_name: 0}
        self.expected_count = expected_count

    @register_step("切换捕虫能力")
    def step1(self):
       ability_manager.change_ability(ABILITY_NAME_INSECT)

    @register_step("开启地图追踪")
    def step2(self):
        material_track.change_tracking_material(self.insect_name)

    @register_step("开始捕虫")
    def step3(self):
        timer = AdvanceTimer(self.time_limit)
        timer.start()
        while not timer.reached() and not self.need_stop() \
        and self.material_count_dict[self.insect_name] < self.expected_count:
            itt.right_down()
            itt.key_down('w')
            while not timer.reached() and not self.need_stop():
                if not material_track.check_tracking_near():
                    degree = material_track.get_material_track_degree()
                    change_view_to_angle(degree, offset=3, use_last_rotation = True)
                else:
                    itt.right_up()
                    itt.key_up('w')
                    time.sleep(0.8) # 等待文字出现
                    text = itt.ocr_single_line(AreaMaterialGetText)
                    print(text)
                    if self.insect_name in text:
                        self.log_to_gui(f"{self.insect_name} x 1")
                        self.material_count_dict[self.insect_name] += 1
                    time.sleep(1) # 等待动作后摇
                    break
        itt.right_up()
        itt.key_up('w')
        self.update_task_result(
            message=f"获得{self.insect_name}x{self.material_count_dict[self.insect_name]}",
            data=self.material_count_dict
        )


if __name__ == "__main__":
    nikki_map.reinit_smallmap()
    calibrate_view_rotation_ratio()
    task = CatchInsectTask("发卡蚂蚱")
    # task.task_run()
    task.step3()