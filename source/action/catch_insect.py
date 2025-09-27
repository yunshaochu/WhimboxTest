from source.task.task_template import TaskTemplate, register_step
from source.interaction.interaction_core import itt
from source.ability.ability import ability_manager
from source.ability.cvar import *
from source.map.track import material_track
from source.map.map import nikki_map
from source.view_and_move.utils import *
from source.view_and_move.view import *

class CatchInsectTask(TaskTemplate):
    def __init__(self, insect_name: str):
        super().__init__("catch_insect_task")
        self.insect_name = insect_name

    @register_step("切换捕虫能力")
    def step1(self):
       ability_manager.change_ability(ABILITY_NAME_INSECT)

    @register_step("开启地图追踪")
    def step2(self):
        material_track.change_tracking_material(self.insect_name)

    @register_step("向最近的材料移动")
    def step3(self):
        itt.right_down()
        itt.key_down('w')
        while not self.task_stop_flag:
            if material_track.check_tracking_near():
                itt.right_up()
                itt.key_up('w')
                break
            degree = material_track.get_material_track_degree()
            change_view_to_angle(degree, offset=3, use_last_rotation = True)

if __name__ == "__main__":
    nikki_map.reinit_smallmap()
    calibrate_view_rotation_ratio()
    task = CatchInsectTask("发卡蚂蚱")
    while True:
        task.step3()
        time.sleep(0.5)