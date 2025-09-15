from source.view_and_move.cvars import *
from source.interaction.interaction_core import itt
from source.ui.ui_assets import *
from source.common.base_threading import AdvanceThreading
from source.common.timer_module import AdvanceTimer
from source.common.logger import logger
from source.common.utils.img_utils import *
from source.common.utils.posi_utils import *
import time


def get_move_mode_in_game(ret_rate=False) -> str:
    """判断当前的移动模式（目前只支持步行和跳跃）"""
    def preprocessing(img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_white = np.array([0, 0, 210])
        upper_white = np.array([180, 50, 255])
        mask = cv2.inRange(hsv, lower_white, upper_white)
        return mask
    
    cap = itt.capture(posi=AreaMovementWalk.position)
    cap = preprocessing(cap)
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


class JumpController(AdvanceThreading):
    def __init__(self):
        super().__init__()
        self.while_sleep = 0.02
        self.normal_jump_timer = AdvanceTimer(0.3)
        self.double_jump_timer = AdvanceTimer(0.1)
        self.in_normal_jump = False
        self.in_prepare_double_jump = False
        self.in_double_jump = False

    def is_jumping(self):
        return self.in_normal_jump or self.in_prepare_double_jump or self.in_double_jump

    def clear_jump_state(self):
        self.in_normal_jump = False
        self.in_prepare_double_jump = False
        self.in_double_jump = False
        # logger.debug('clear jump state')

    def start_jump(self):
        if self.is_jumping():
            # logger.debug('already jumping')
            return
        itt.key_down('spacebar')
        self.in_normal_jump = True
        self.in_prepare_double_jump = False
        self.in_double_jump = False
        self.normal_jump_timer.reset()
        self.normal_jump_timer.start()
        logger.debug('start jump')

    def _prepare_double_jump(self):
        itt.key_up('spacebar')
        self.in_normal_jump = False
        self.in_prepare_double_jump = True
        self.in_double_jump = False
        self.double_jump_timer.reset()
        self.double_jump_timer.start()
        logger.debug('prepare double jump')

    def _start_double_jump(self):
        itt.key_press('spacebar')
        self.in_normal_jump = False
        self.in_prepare_double_jump = False
        self.in_double_jump = True
        logger.debug('start double jump')

    def stop_jump(self):
        if self.in_normal_jump:
            itt.key_up('spacebar')
            self.normal_jump_timer.reset()
            self.in_normal_jump = False
            logger.debug('stop jump')
        if self.in_prepare_double_jump:
            self.in_prepare_double_jump = False
            logger.debug("stop prepare double jump")
        if self.in_double_jump:
            itt.key_press('spacebar')
            self.in_double_jump = False
            logger.debug('stop double jump')

    def switch_jump(self):
        if self.in_normal_jump and self.normal_jump_timer.reached():
            self._prepare_double_jump()
        if self.in_prepare_double_jump and self.double_jump_timer.reached():
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

    def start_move_ahead(self, current_posi, target_posi):
        # 估算移动速度
        now_time = time.time()
        if self.last_posi != None:
            distance = euclidean_distance(self.last_posi, current_posi)
            if distance != 0:
                cost_time = now_time - self.last_posi_time
                move_speed = distance / cost_time
                self._update_move_speed(move_speed)
        self.last_posi = current_posi
        self.last_posi_time = now_time

        # 估算移动时间
        speed = self._estimate_move_speed()
        duration = euclidean_distance(current_posi, target_posi) / speed
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
    while True:
        print(get_move_mode_in_game(ret_rate=True))
        time.sleep(0.2)