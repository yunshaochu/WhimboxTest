from source.interaction.interaction_core import itt
from source.action.material_track_base import MaterialTrackBaseTask
from source.common.utils.ui_utils import *

class CatchInsectTask(MaterialTrackBaseTask):
    def __init__(self, insect_name, expected_count=1, check_stop_func=None):
        super().__init__(insect_name, expected_count, check_stop_func)

    def pre_play_func(self):
        pass

    def post_play_func(self):
        time.sleep(0.8) # 等待捕虫动作结束


if __name__ == "__main__":
    from source.map.map import nikki_map
    from source.view_and_move.view import calibrate_view_rotation_ratio
    nikki_map.reinit_smallmap()
    calibrate_view_rotation_ratio()
    task = CatchInsectTask("发卡蚱蜢", 2)
    # task.task_run()
    task.step3()