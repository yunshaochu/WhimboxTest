import time
from enum import Enum
import cv2

from source.common.cvars import CV_DEBUG_MODE
from source.common.utils.ui_utils import wait_until_appear
from source.task.task_template import TaskTemplate, register_step
from source.interaction.interaction_core import itt
from source.ui.page_assets import page_main
from source.ui.ui import ui_control
from source.ui.ui_assets import (
    IconFishingNoFish,
    IconFishingPullLine,
    IconFishingPullLineAlt,
    IconFishingReelIn,
    IconFishingReelLine,
    IconFishingStrike,
    AreaFishingDetection,
    IconFishingSkip,
    TextClickSkip,
)
from source.common.utils.img_utils import count_px_with_hsv_limit
from source.common.utils.asset_utils import asset_get_bbox
from source.common.utils.posi_utils import union_bbox
from source.ability.ability import ability_manager
from source.ability.cvar import ABILITY_NAME_FISH
from source.common.logger import logger

hsv_limit = ([20, 50, 245], [30, 90, 255])

class FishingState(Enum):
    NOT_FISHING = 0
    REEL_IN = 1       # 收竿 (右键取消)
    STRIKE = 2      # 提竿 (S)
    PULL_LINE = 3     # 拉扯鱼线 (A/D)
    REEL_LINE = 4     # 收线 (右键狂点)
    SKIP = 5          # 跳过 (F)
    UNKNOWN = 6

class FishingTask(TaskTemplate):
    STATE_MAPPING = [
        (IconFishingStrike, FishingState.STRIKE),
        (IconFishingReelIn, FishingState.REEL_IN),
        (IconFishingPullLine, FishingState.PULL_LINE),
        (IconFishingPullLineAlt, FishingState.PULL_LINE),
        (IconFishingReelLine, FishingState.REEL_LINE),
        (IconFishingSkip, FishingState.SKIP),
    ]
    def __init__(self):
        super().__init__("fishing_task")
        self.state_area = self.get_state_area()

    def get_state_area(self):
        """获取状态判断区域"""
        bboxes = []
        for icon, _ in self.STATE_MAPPING:
            bboxes.append(icon.bbg_posi)
        merged_bbox = union_bbox(*bboxes)
        return merged_bbox

    def get_current_state(self):
        """在模板区域内检测当前状态"""
        cap = itt.capture(posi=self.state_area)
        _, cap = cv2.threshold(cap, 210, 255, cv2.THRESH_BINARY)
        if CV_DEBUG_MODE:
            cv2.imshow("cap", cap)
            cv2.waitKey(1)

        for icon, state in self.STATE_MAPPING:
            if itt.get_img_existence(icon, is_gray=True, cap=cap):
                return state

        return FishingState.UNKNOWN

    def _pull_in_direction(self, key, px_count):
        """
        按下一个按键并检查方向是否正确。
        如果正确，则持续按住
        """
        itt.key_down(key)
        while True:
            time.sleep(0.3)
            cap = itt.capture(posi=AreaFishingDetection.position)
            current_px_count = count_px_with_hsv_limit(cap, hsv_limit[0], hsv_limit[1])
            if current_px_count < px_count:
                logger.debug(f"方向正确: {key}, {px_count} -> {current_px_count}")
                px_count = current_px_count
                if px_count == 0:
                    break
                continue
            else:
                break
        itt.key_up(key)
        return px_count

    def handle_pull_line(self):
        """处理拉扯鱼线状态的核心逻辑"""
        self.log_to_gui("进入拉扯鱼线状态")
        cap = itt.capture(posi=AreaFishingDetection.position)
        px_count = count_px_with_hsv_limit(cap, hsv_limit[0], hsv_limit[1])
        while px_count > 0:
            px_count = self._pull_in_direction('a', px_count)
            if px_count == 0:
                break
            px_count = self._pull_in_direction('d', px_count)
            if px_count == 0:
                break

    def handle_strike(self):
        self.log_to_gui("状态: 提竿")
        itt.key_press('s')

    def handle_reel_line(self):
        self.log_to_gui("状态: 收线")
        while True:
            itt.right_click()
            if self.get_current_state() != FishingState.REEL_LINE:
                break
            # time.sleep(0.1)

    def handle_skip(self):
        self.log_to_gui("状态: 跳过")
        while not ui_control.verify_page(page_main):
            itt.key_press('f')
            time.sleep(0.2)

    @register_step("朝向钓鱼点位")
    def step1(self):
        pass

    @register_step("切换钓鱼能力")
    def step2(self):
        ability_manager.change_ability(ABILITY_NAME_FISH)

    @register_step("开始钓鱼")
    def step3(self):
        itt.right_click()
        time.sleep(3)
        if itt.get_img_existence(IconFishingNoFish):
            itt.right_click()
            while not ui_control.verify_page(page_main):
                time.sleep(0.2)
            self.update_task_result(message="鱼已经被钓光了")
            return

        while True:
            state = self.get_current_state()

            if state in [FishingState.NOT_FISHING, FishingState.UNKNOWN, FishingState.REEL_IN]:
                time.sleep(0.5)
                continue
            elif state == FishingState.STRIKE:
                self.handle_strike()
                continue
            elif state == FishingState.PULL_LINE:
                self.handle_pull_line()
                continue
            elif state == FishingState.REEL_LINE:
                self.handle_reel_line()
                continue
            elif state == FishingState.SKIP:
                self.handle_skip()
                break
        
        self.update_task_result(message="钓鱼任务完成")
        self.log_to_gui("钓鱼任务完成")


if __name__ == "__main__":
    # while True:
    #     time.sleep(5)
    #     fishing_task = FishingTask()
    #     fishing_task.task_run()
    task = FishingTask()
    task.step3()

# todo:
# 1. 接受朝向参数，自动调整朝向
# 2. 在该朝向经过一段时间无响应后，自动微调朝向或结束任务
# 3. 默认连续钓鱼3次
# 4. 接入自动跑图，钓鱼结果记录