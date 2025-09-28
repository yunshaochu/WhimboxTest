from source.interaction.interaction_core import itt
from source.action.material_track_base import MaterialTrackBaseTask
from source.common.utils.ui_utils import *

class CleanAnimalTask(MaterialTrackBaseTask):
    def __init__(self, animal_name, expected_count=1, check_stop_func=None):
        super().__init__(animal_name, expected_count, check_stop_func)

    def pre_play_func(self):
        # 主动按F跳过清洁动画
        if wait_until_appear(TextFSkip):
            itt.key_press('f')
    
    def post_play_func(self):
        pass

if __name__ == "__main__":
    from source.map.map import nikki_map
    from source.view_and_move.view import calibrate_view_rotation_ratio
    nikki_map.reinit_smallmap()
    calibrate_view_rotation_ratio()
    task = CleanAnimalTask("汪汪毛线", expected_count=2)
    # task.task_run()
    task.step3()