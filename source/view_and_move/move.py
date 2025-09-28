from source.view_and_move.cvars import *
from source.interaction.interaction_core import itt
from source.ui.ui_assets import *
from source.common.base_threading import AdvanceThreading
from source.common.timer_module import AdvanceTimer
from source.common.logger import logger
from source.common.utils.img_utils import *
from source.common.utils.posi_utils import *

import time
from enum import Enum

def get_move_mode_in_game(ret_rate=False) -> str:
    """判断当前的移动模式（目前只支持步行和跳跃）"""
    cap = itt.capture(posi=AreaMovementWalk.position)
    lower_white = np.array([0, 0, 210])
    upper_white = np.array([180, 50, 255])
    cap = process_with_hsv_limit(cap, lower_white, upper_white)
    r = similar_img(cap, IconMovementWalking.image[:, :, 0])
    if CV_DEBUG_MODE:
        cv2.imshow('cap', cap)
        cv2.waitKey(1)
    if ret_rate:
        if r > 0.95:
            return MOVE_MODE_WALK, r
        else:
            return MOVE_MODE_JUMP, r
    else:
        if r > 0.95:
            return MOVE_MODE_WALK
        else:
            return MOVE_MODE_JUMP


class JumpState(Enum):
    IDLE = 0
    NORMAL_JUMP = 1
    PREPARE_DOUBLE_JUMP = 2
    DOUBLE_JUMP = 3

class JumpController(AdvanceThreading):
    def __init__(self):
        super().__init__()
        self.while_sleep = 0.02
        self.normal_jump_timer = AdvanceTimer(0.3)
        self.prepare_double_jump_timer = AdvanceTimer(0.1)
        self._jump_state = JumpState.IDLE

    def is_jumping(self):
        return self._jump_state != JumpState.IDLE

    def is_double_jumping(self):
        return self._jump_state == JumpState.DOUBLE_JUMP

    def clear_jump_state(self):
        self._jump_state = JumpState.IDLE
        self.normal_jump_timer.reset()
        self.prepare_double_jump_timer.reset()
        logger.debug('clear jump state')

    def start_jump(self):
        if self.is_jumping():
            logger.debug('already jumping')
            return
        self._jump_state = JumpState.NORMAL_JUMP
        self.normal_jump_timer.reset()
        self.normal_jump_timer.start()
        itt.key_down('spacebar')
        logger.debug('start jump')

    def _prepare_double_jump(self):
        self._jump_state = JumpState.PREPARE_DOUBLE_JUMP
        self.prepare_double_jump_timer.reset()
        self.prepare_double_jump_timer.start()
        itt.key_up('spacebar')
        logger.debug('prepare double jump')

    def _start_double_jump(self):
        self._jump_state = JumpState.DOUBLE_JUMP
        itt.key_press('spacebar')
        logger.debug('start double jump')

    def stop_jump(self):
        if self._jump_state == JumpState.IDLE or get_move_mode_in_game() == MOVE_MODE_WALK:
            return
        if self._jump_state == JumpState.NORMAL_JUMP:
            itt.key_up('spacebar')
            self.normal_jump_timer.reset()
            self._jump_state = JumpState.IDLE
            logger.debug('stop jump')
        elif self._jump_state == JumpState.PREPARE_DOUBLE_JUMP:
            self._jump_state = JumpState.IDLE
            logger.debug("stop prepare double jump")
        elif self._jump_state == JumpState.DOUBLE_JUMP:
            itt.key_press('spacebar')
            self._jump_state = JumpState.IDLE
            logger.debug('stop double jump')

    def switch_jump(self):
        if self._jump_state == JumpState.NORMAL_JUMP and self.normal_jump_timer.reached():
            self._prepare_double_jump()
        elif self._jump_state == JumpState.PREPARE_DOUBLE_JUMP and self.prepare_double_jump_timer.reached():
            self._start_double_jump()

    def loop(self):
        self.switch_jump()


class MoveController(AdvanceThreading):
    def __init__(self):
        super().__init__()
        self.while_sleep = 0.02
        self.move_ahead_timer = None
        self.is_moving = False
        self.last_posi = None
        self.last_posi_time = 0
        # self.move_speed = 12 # 默认移动速度：12px/s
        self.move_speed_list = [12 for i in range(5)]

    def _update_move_speed(self, speed):
        self.move_speed_list.append(speed)
        self.move_speed_list.pop(0)

    def _estimate_move_speed(self):
        # 去掉最大值和最小值，剩余取平均值
        return (sum(self.move_speed_list) - max(self.move_speed_list) - min(self.move_speed_list)) / (len(self.move_speed_list) - 2)

    def start_move_ahead(self, current_posi, target_posi, offset):
        # 更新历史移动速度
        now_time = time.time()
        if self.last_posi != None:
            distance = euclidean_distance(self.last_posi, current_posi)
            if distance > 1:
                cost_time = now_time - self.last_posi_time
                move_speed = distance / cost_time
                self._update_move_speed(move_speed)
        self.last_posi = current_posi
        self.last_posi_time = now_time

        # 估算移动时间
        speed = self._estimate_move_speed()
        target_dist = euclidean_distance(current_posi, target_posi)
        # 减去magic数字，避免移动过头
        # todo: 根据电脑性能动态计算这个magic，大致等于一次auto_path_task的inner_step循环的耗时。可能还有其他更好的预估移动时间的方式
        duration = target_dist / speed - 0.2
        # if target_dist < offset:
        #     duration /= 2
        #     logger.debug(f"distance to target is less than offset, move slowly")
        # logger.debug(f"move speed: {speed}, duration: {duration}")

        # 开始移动
        itt.key_down('w')
        self.is_moving = True
        self.move_ahead_timer = AdvanceTimer(duration).start()

    def stop_move_ahead(self):
        self.is_moving = False
        self.move_ahead_timer = None
        self.last_posi = None # 让下次开始移动时，速度延用停止移动前的估算速度
        itt.key_up('w')

    def switch_move(self):
        if self.is_moving and self.move_ahead_timer.reached():
            itt.key_up('w')
            self.is_moving = False

    def loop(self):
        self.switch_move()

if __name__ == "__main__":
    # jump_controller = JumpController()
    # jump_controller.start()
    # while True:
    #     jump_controller.start_jump()
    #     time.sleep(1)
    #     jump_controller.stop_jump()
    #     time.sleep(3)

    while True:
        print(get_move_mode_in_game())
        time.sleep(0.3)