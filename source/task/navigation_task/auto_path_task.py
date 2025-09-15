"""自动寻路"""

from re import DEBUG
from source.task.task_template import TaskTemplate, register_step
from source.interaction.interaction_core import itt
import time, os
from source.task.utils import *
from source.common.path_lib import *
from source.task.navigation_task.common import *
from source.map.map import nikki_map
from source.view_and_move.view import *
from source.view_and_move.move import *
from source.action.pickup import PickupTask

class AutoPathTask(TaskTemplate):
    def __init__(self, path_file_name):
        super().__init__("auto_path_task")
        self.step_sleep = 0
        with open(os.path.join(ASSETS_PATH, "paths", path_file_name), "r", encoding="utf-8") as f:
            path_record = PathRecord.model_validate_json(f.read())
            self.path_info = path_record.info
            self.path_points = path_record.points
        
        # 各种状态记录
        self.last_position = None
        self.curr_position = None
        self.curr_target_point_id = 0
        self.target_point: PathPoint = None
        self.need_move_mode = MOVE_MODE_WALK
        self.last_need_move_mode = MOVE_MODE_WALK
        self.last_game_move_mode = MOVE_MODE_WALK

        self.jump_controller = JumpController()
        self.move_controller = MoveController()

        # 一些常量
        self.stop_move_time = 0.2
        self.offset = 2.5 # 当距离必经点offset以内，就视作已经到达


    def _update_next_target_point(self):
        """更新下一个必经点"""
        if self.curr_target_point_id < len(self.path_points) - 1:
            for index in range(self.curr_target_point_id+1, len(self.path_points)):
                if self.path_points[index].point_type == POINT_TYPE_TARGET:
                    self.curr_target_point_id = index
                    self.target_point = self.path_points[index]
                    return
    
    def start_move(self, current_posi, target_posi):
        # itt.key_down('w')
        self.move_controller.start_move_ahead(current_posi, target_posi)

    def stop_move(self):
        # itt.key_up('w')
        self.move_controller.stop_move_ahead()

    def is_moving(self):
        return self.move_controller.is_moving

    def start_jump(self):
        self.jump_controller.start_jump()

    def stop_jump(self):
        self.jump_controller.stop_jump()


    @register_step("初始化各种信息")
    def step0(self):
        # 初始化地图信息
        nikki_map.reinit_smallmap()
        self.curr_position = nikki_map.get_position(use_cache=True)
        # 校准视角旋转比例
        calibrate_view_rotation_ratio()
        # 启动动作控制线程
        self.jump_controller.start_threading()
        self.move_controller.start_threading()


    @register_step("自动寻路中……")
    def step1(self):
        last_t = time.time()
        while not self.task_stop_flag:
            if DEBUG_MODE:
                t = time.time()
                print(f"cost {round(t - last_t, 2)}")
                last_t = t
            is_end = self.inner_step_update_target()
            if is_end:
                break
            self.inner_step_change_view()
            self.inner_step_control_move()
        return "step2"


    def inner_step_update_target(self):
        is_end = False
        self.last_position = self.curr_position
        self.curr_position = nikki_map.get_position()
        self.target_point = self.path_points[self.curr_target_point_id]

        # 计算当前位置与必经点的距离
        # 只根据当前位置计算距离，会出现一种情况：
        # 已经走过了必经点，导致离必经点的距离会越走越远
        # 所以要结合上次的位置，计算离必经点的最小距离
        if self.last_position is not None:
            equal_points = linspace(self.last_position, self.curr_position)
            min_dist = euclidean_distance_plist(self.target_point.position, equal_points).min()
            target_dist = min_dist
        else:
            target_dist = euclidean_distance(self.target_point.position, self.curr_position)
        
        if target_dist <= self.offset:
            if self.curr_target_point_id >= len(self.path_points) - 1:
                # 走到终点了
                is_end = True
            else:
                # 处理各种ACTION
                if self.target_point.action:
                    self.stop_move()
                    self.stop_jump()
                    if self.target_point.action == ACTION_PICK_UP:
                        pickup_task = PickupTask()
                        task_result = pickup_task.task_run()
                    elif self.target_point.action == ACTION_WAIT:
                        wait_time = self.target_point.action_params
                        if wait_time is None:
                            wait_time = self.stop_move_time
                        time.sleep(float(wait_time))
                    
                # 当行动模式切换时，停一下，避免惯性导致踏空
                self.need_move_mode = self.target_point.move_mode
                if self.last_need_move_mode != self.need_move_mode and self.is_moving():
                    self.stop_move()
                    time.sleep(self.stop_move_time)
                self.last_need_move_mode = self.need_move_mode
                self._update_next_target_point()
        
        if self.target_point.action == ACTION_TELEPORT:
            if target_dist >= not_teleport_offset:
                self.log_to_gui(f"传送到附近的流转之柱")
                self.stop_move()
                self.stop_jump()
                nikki_map.bigmap_tp(self.target_point.position)
                self.curr_position = nikki_map.get_position()
        return is_end


    def inner_step_change_view(self):
        self.curr_position = nikki_map.get_position()
        target_degree = calculate_posi2degree(self.curr_position, self.target_point.position)
        delta_degree = abs(calculate_delta_angle(nikki_map.get_rotation(), target_degree))
        # 如果要转很大的角度，需要先停下来
        if delta_degree >= 45 and self.is_moving():
            self.stop_move()
        change_view_to_angle(target_degree, offset=5, use_last_rotation = True)


    def inner_step_control_move(self):
        game_move_mode = get_move_mode_in_game()
        # 游戏中二段跳瞬间，会出现一帧WALK状态的图标，
        # 所以这里需要判断连续两帧都是WALK，避免误判
        if game_move_mode == MOVE_MODE_WALK and self.last_game_move_mode == MOVE_MODE_WALK:
            self.jump_controller.clear_jump_state()
            
        if self.need_move_mode == MOVE_MODE_WALK:
            if game_move_mode == MOVE_MODE_JUMP:
                self.stop_jump()
        elif self.need_move_mode == MOVE_MODE_JUMP:
            if game_move_mode == MOVE_MODE_WALK:
                self.start_jump()
        
        self.last_game_move_mode = game_move_mode
        self.start_move(self.curr_position, self.target_point.position)
        

    @register_step("结束自动寻路")
    def step2(self):
        self.stop_move()
        self.stop_jump()
        self.jump_controller.stop_threading()
        self.move_controller.stop_threading()


    def handle_exception(self, e):
        self.jump_controller.stop_threading()
        self.move_controller.stop_threading()


if __name__ == "__main__":
    task = AutoPathTask("example.json")
    task.task_run()