"""
路线记录（开发者工具）
"""

from source.task.task_template import TaskTemplate, register_step
from source.ui.ui import ui_control
from source.ui.page_assets import *
import time
from source.common.path_lib import *
from source.map.map import nikki_map
from threading import Lock
import os
from source.task.navigation_task.rdp import rdp_optimize
from source.task.navigation_task.common import *
from source.view_and_move.move import *
from source.view_and_move.view import *
from source.common.utils.utils import save_json


class RecordPathTask(TaskTemplate):
    def __init__(self):
        super().__init__("record_path_task")
        self.step_sleep = 0.05
        self.min_gap = 2    # 路径点最小间隔距离
        self._lock = Lock()
        # self.last_direction = 0
        # self.last_target_position = None # 上一个必经点
        self.path_point_list = []
        self.add_hotkey(';', self.recognize)


    def recognize(self):
        # if itt.get_text_existence(TextFPickUp):
        #     self.log_to_gui(f"识别到采集点，已记录")
        #     self._add_point(nikki_map.get_position(), POINT_TYPE_TARGET, MOVE_MODE_WALK, ACTION_PICK_UP)
        self._add_point(nikki_map.get_position(), POINT_TYPE_TARGET, MOVE_MODE_WALK, ACTION_PICK_UP)
        self.log_to_gui(f"记录点位成功")


    def _get_all_position(self):
        position_list = []
        for pp in self.path_point_list:
            position_list.append(pp.position)
        return position_list


    def _add_point(self, position, point_type=POINT_TYPE_PASS, move_mode=None, action=None, action_params=None):
        with self._lock:
            if move_mode == None:
                move_mode = get_move_mode_in_game()
            # 如果移动模式切换，就记录为target
            if len(self.path_point_list) > 0 and self.path_point_list[-1].move_mode != move_mode:
                point_type = POINT_TYPE_TARGET
            pp = PathPoint(
                id=len(self.path_point_list),
                move_mode=move_mode,
                point_type=point_type,
                action=action,
                action_params=action_params,
                position=position
            )
            self.path_point_list.append(pp)


    @register_step("准备中，请稍等")
    def step1(self):
        nikki_map.reinit_smallmap()
        current_posi = nikki_map.get_position()
        closest_teleporter = nikki_map.find_closest_teleporter(current_posi, nikki_map.map_name)
        distance = euclidean_distance(current_posi, closest_teleporter.position)
        if distance < not_teleport_offset:
            self._add_point(current_posi, POINT_TYPE_TARGET, MOVE_MODE_WALK, ACTION_TELEPORT)
        else:
            raise Exception("起点与最近的传送点太远了，不予记录")


    @register_step("开始录制，按“分号”记录特殊点位")
    def step2(self):
        while True:
            time.sleep(self.step_sleep)
            if self.need_stop():
                break
            if not ui_control.verify_page(page_main):
                continue

            all_posi = self._get_all_position()
            curr_posi = nikki_map.get_position()

            # 计算当前位置与上个路径点的最短距离
            if len(all_posi)>=1:
                dist = euclidean_distance(curr_posi, all_posi[-1])
            else:
                dist = 99999

            if dist >= self.min_gap:
                self._add_point(curr_posi)
        self.save_path()


    def save_path(self):
        end_position = nikki_map.get_position()
        self._add_point(end_position, POINT_TYPE_TARGET)

        # 优化路线
        optimize_path(self.path_point_list)

        # 保存路线
        now = time.localtime(time.time())
        date_str = time.strftime("%Y%m%d%H%M%S", now)
        name = f"我的路线_{date_str}"
        json_name = f"{name}.json"
        region_name, map_name = nikki_map.update_region_and_map_name(use_cache=True)
        path_record = PathRecord(
            info=PathInfo(
                name=name, 
                type="", 
                target="",
                region=region_name,
                map=map_name,
            ),
            points=self.path_point_list
        )
        save_path = os.path.join(ASSETS_PATH, "paths")
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        save_json(path_record.model_dump(), json_name, save_path)
        logger.info(f"路线保存成功，路径：{os.path.join(save_path, json_name)}")
        self.update_task_result(message=f"录制成功，路线名：{name}")


def optimize_path(path_point_list):
    # 游戏中二段跳瞬间，会出现一帧WALK状态的图标，这里粗略检查一下
    for i in range(len(path_point_list)-1):
        curr_move_mode = path_point_list[i].move_mode
        if curr_move_mode == MOVE_MODE_WALK and i-2 > 0 and i+1 < len(path_point_list):
            prev_move_mode = path_point_list[i-1].move_mode
            prev2_move_mode = path_point_list[i-2].move_mode
            next_move_mode = path_point_list[i+1].move_mode
            if prev2_move_mode == MOVE_MODE_WALK and prev_move_mode == MOVE_MODE_JUMP and next_move_mode == MOVE_MODE_JUMP:
                path_point_list[i].move_mode = MOVE_MODE_JUMP

    # 找出target之间转折过大的点，也设为target
    start_target_point_index = -1
    end_target_point_index = -1
    index = -1
    while index < len(path_point_list)-1:
        index += 1
        pp = path_point_list[index]

        if pp.point_type == POINT_TYPE_TARGET:

            if start_target_point_index == -1:
                start_target_point_index = index
                continue

            if end_target_point_index == -1:
                end_target_point_index = index
                rdp_optimize(path_point_list, start_target_point_index, end_target_point_index, 1)
                start_target_point_index = index
                end_target_point_index = -1


if __name__ == "__main__":
    task = RecordPathTask()
    task.task_run()