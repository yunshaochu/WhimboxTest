import time
from enum import Enum
import cv2

from source.task.task_template import TaskTemplate, register_step
from source.interaction.interaction_core import itt
from source.ui.ui_assets import (
    IconFishingPullLine,
    IconFishingPullLineAlt,
    IconFishingReelIn,
    IconFishingReelLine,
    IconFishingStrike,
    AreaFishingDetection,
    IconFishingSkip,
)
from source.common.utils.img_utils import calculate_hsv_area
from source.common.utils.asset_utils import asset_get_bbox
from source.common.utils.posi_utils import union_bbox

class FishingState(Enum):
    NOT_FISHING = 0
    REEL_IN = 1       # 收竿 (S)
    STRIKING = 2      # 提竿 (S)
    PULL_LINE = 3     # 拉扯鱼线 (A/D)
    REEL_LINE = 4     # 收线 (Right-click)
    SKIP = 5          # 跳过 (F)
    UNKNOWN = 6

class FishingTask(TaskTemplate):
    STATE_MAPPING = [
        (IconFishingStrike, FishingState.STRIKING),
        (IconFishingReelIn, FishingState.REEL_IN),
        (IconFishingPullLine, FishingState.PULL_LINE),
        (IconFishingPullLineAlt, FishingState.PULL_LINE),
        (IconFishingReelLine, FishingState.REEL_LINE),
        (IconFishingSkip, FishingState.SKIP),
    ]
    def __init__(self):
        super().__init__("fishing_task")
        self.last_area = 0
        self.tpl_area = None

    def get_tpl_area(self):
        """获取模板状态判断区域"""
        if self.tpl_area:
            return self.tpl_area
        
        bboxes = []
        for icon, _ in self.STATE_MAPPING:
            cap = itt.capture(posi=icon.cap_posi)
            if cap is not None and cap.size > 0:
                bbox = asset_get_bbox(cap)
                if bbox and bbox[2] > bbox[0] and bbox[3] > bbox[1]:  # 有效边界
                    # 转换到全局坐标系
                    global_bbox = [
                        icon.cap_posi[0] + bbox[0],
                        icon.cap_posi[1] + bbox[1], 
                        icon.cap_posi[0] + bbox[2],
                        icon.cap_posi[1] + bbox[3]
                    ]
                    bboxes.append(global_bbox)
        
        if not bboxes:
            return None
        
        merged_bbox = union_bbox(*bboxes)
        
        self.tpl_area = merged_bbox
        return merged_bbox

    def get_current_state(self, tpl_area):
        """在模板区域内检测当前状态"""
        if tpl_area is None:
            return FishingState.NOT_FISHING

        cap = itt.capture(posi=tpl_area)
        _, cap = cv2.threshold(cap, 210, 255, cv2.THRESH_BINARY)

        for icon, state in self.STATE_MAPPING:
            if itt.get_img_existence(icon, is_gray=True, cap=cap):
                return state

        return FishingState.UNKNOWN

    def _pull_in_direction(self, key, hsv_area, initial_area):
        """
        按下一个按键并检查方向是否正确。
        如果正确，则持续按住
        """
        itt.key_down(key)
        itt.delay(0.3, is_log=False)
        
        current_area = calculate_hsv_area(itt.capture(posi=hsv_area))
        
        if current_area < initial_area - 5:
            self.log_to_gui(f"方向正确: {key.upper()}")
            while current_area < initial_area - 5:
                if self.get_current_state(self.get_tpl_area()) != FishingState.PULL_LINE:
                    break
                initial_area = current_area
                itt.delay(0.2, is_log=False)
                current_area = calculate_hsv_area(itt.capture(posi=hsv_area))
            
            itt.key_up(key)
            return True
        else:
            itt.key_up(key)
            return False

    def handle_pull_line(self):
        """处理拉扯鱼线状态的核心逻辑"""
        cap = itt.capture(posi=AreaFishingDetection.cap_posi)
        if cap is None or cap.size == 0:
            self.log_to_gui("错误：无法获取到HSV区域")
            return
            
        hsv_area = asset_get_bbox(cap)
        if not hsv_area or hsv_area[2] <= hsv_area[0] or hsv_area[3] <= hsv_area[1]:
            self.log_to_gui("错误：未找到有效的HSV区域（AreaFishingDetection）")
            return
            
        hsv_area = [
            AreaFishingDetection.cap_posi[0] + hsv_area[0],
            AreaFishingDetection.cap_posi[1] + hsv_area[1],
            AreaFishingDetection.cap_posi[0] + hsv_area[2], 
            AreaFishingDetection.cap_posi[1] + hsv_area[3]
        ]

        self.log_to_gui("进入拉扯鱼线状态")
        
        while True:
            current_state = self.get_current_state(self.get_tpl_area())
            if current_state != FishingState.PULL_LINE:
                self.log_to_gui(f"拉扯鱼线中断，进入状态: {current_state.name}")
                return

            initial_area = calculate_hsv_area(itt.capture(posi=hsv_area))
            if initial_area == 0:
                break

            if self._pull_in_direction('a', hsv_area, initial_area):
                continue
            if self._pull_in_direction('d', hsv_area, initial_area):
                continue
            
            self.log_to_gui("方向错误，重新试探")

    def handle_reel_in_or_striking(self):
        self.log_to_gui("状态: 收竿/提竿, 按下 S")
        itt.key_down('s')
        itt.delay(0.1)
        itt.key_up('s')
        itt.delay(0.1)

    def handle_reel_line(self):
        self.log_to_gui("状态: 收线, 点击右键")
        for _ in range(10):
            if self.get_current_state(self.get_tpl_area()) != FishingState.REEL_LINE:
                break
            itt.right_click()
            itt.delay(0.1, is_log=False)
        itt.delay(0.8)

    def handle_skip(self):
        self.log_to_gui("状态: 跳过, 循环按 F 直到黑屏")
        while True:
            itt.key_press('f')
            itt.delay(0.1)  
            self.tpl_area = None
            current_tpl_area = self.get_tpl_area()

            if current_tpl_area is None:
                self.log_to_gui("跳过阶段完成")
                return

    @register_step("开始钓鱼")
    def fishing_loop(self):
        self.log_to_gui("开始钓鱼任务")
        itt.right_click()
        self.log_to_gui("已按下右键开始钓鱼")
        itt.delay(5, comment="等待鱼上钩")
        time.sleep(5)

        while True:
            tpl_area = self.get_tpl_area()
            state = self.get_current_state(tpl_area)
            self.log_to_gui(f"当前状态: {state.name}")

            if state == FishingState.NOT_FISHING or state == FishingState.UNKNOWN:
                #self.log_to_gui("钓鱼状态未知，跳过")
                continue
            elif state in [FishingState.REEL_IN, FishingState.STRIKING]:
                self.handle_reel_in_or_striking()
            elif state == FishingState.PULL_LINE:
                self.handle_pull_line()
            elif state == FishingState.REEL_LINE:
                self.handle_reel_line()
            elif state == FishingState.SKIP:
                self.handle_skip()
                break 
        
        self.update_task_result(message="钓鱼任务完成")
        self.log_to_gui("钓鱼任务完成")


if __name__ == "__main__":
    while True:
        time.sleep(5)
        fishing_task = FishingTask()
        fishing_task.task_run()
