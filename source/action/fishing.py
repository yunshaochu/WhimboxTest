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
    TextFSkip,
)
from source.common.utils.img_utils import calculate_hsv_area
from source.common.utils.asset_utils import asset_get_bbox
from source.common.utils.posi_utils import union_bbox
from source.common.cvars import DEBUG_MODE

class FishingState(Enum):
    NOT_FISHING = 0
    REEL_IN = 1       # 收竿 (no action)
    STRIKING = 2      # 提竿 (S)
    PULL_LINE = 3     # 拉扯鱼线 (A/D)
    REEL_LINE = 4     # 收线 (Right-click)
    SKIP = 5          # 跳过 (F)
    UNKNOWN = 6

class FishingTask(TaskTemplate):
    def __init__(self):
        super().__init__("fishing_task")
        self.last_area = 0
        self.a_area = None

    def get_a_area(self):
        """获取A区域"""
        if self.a_area:
            return self.a_area
        
        bboxes = []
        for icon in [IconFishingPullLine, IconFishingPullLineAlt, IconFishingReelIn, IconFishingReelLine, IconFishingStrike]:
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
        
        self.a_area = merged_bbox
        return merged_bbox

    def get_current_state(self, a_area):
        """在A区域内检测当前状态"""
        if a_area is None:
            if itt.appear(TextFSkip):
                return FishingState.SKIP
            return FishingState.NOT_FISHING


        cap = itt.capture(posi=a_area)
        _, cap = cv2.threshold(cap, 210, 255, cv2.THRESH_BINARY)

        if itt.get_img_existence(IconFishingStrike, is_gray=True, cap=cap):
            return FishingState.STRIKING
        if itt.get_img_existence(IconFishingReelIn, is_gray=True,cap=cap):
            return FishingState.REEL_IN
        if itt.get_img_existence(IconFishingPullLine,is_gray=True, cap=cap):
            return FishingState.PULL_LINE
        if itt.get_img_existence(IconFishingPullLineAlt,is_gray=True, cap=cap):
            return FishingState.PULL_LINE
        if itt.get_img_existence(IconFishingReelLine,is_gray=True, cap=cap):
            return FishingState.REEL_LINE
        if itt.appear(TextFSkip):
             return FishingState.SKIP

        return FishingState.UNKNOWN

    def handle_pull_line(self):
        """处理拉扯鱼线状态的核心逻辑"""
        # 使用 asset_get_bbox 获取B区域
        cap = itt.capture(posi=AreaFishingDetection.cap_posi)
        if cap is None or cap.size == 0:
            self.log_to_gui("错误：无法获取到B区域")
            return
            
        b_area = asset_get_bbox(cap)
        if not b_area or b_area[2] <= b_area[0] or b_area[3] <= b_area[1]:
            self.log_to_gui("错误：未找到有效的B区域（AreaFishingDetection）")
            return
            
        # 转换到全局坐标系
        b_area = [
            AreaFishingDetection.cap_posi[0] + b_area[0],
            AreaFishingDetection.cap_posi[1] + b_area[1],
            AreaFishingDetection.cap_posi[0] + b_area[2], 
            AreaFishingDetection.cap_posi[1] + b_area[3]
        ]

        self.log_to_gui("进入拉扯鱼线状态")
        current_key = None
        
        while True:
            a_area = self.get_a_area()
            current_state = self.get_current_state(a_area)
            if current_state != FishingState.PULL_LINE:
                if current_key:
                    itt.key_up(current_key)
                self.log_to_gui(f"拉扯鱼线中断，进入状态: {current_state.name}")
                return

            initial_area = calculate_hsv_area(itt.capture(posi=b_area))
            if initial_area == 0:
                self.log_to_gui("鱼线拉扯完成")
                if current_key:
                    itt.key_up(current_key)
                break

            # --- 尝试A键 ---
            itt.key_down('a')
            itt.delay(0.3, is_log=False)
            area_after_a = calculate_hsv_area(itt.capture(posi=b_area))

            if area_after_a < initial_area - 5:
                self.log_to_gui("方向正确: A")
                current_key = 'a'
                while area_after_a < initial_area - 5:
                    if self.get_current_state(self.get_a_area()) != FishingState.PULL_LINE:
                        break
                    initial_area = area_after_a
                    itt.delay(0.2, is_log=False)
                    area_after_a = calculate_hsv_area(itt.capture(posi=b_area))
                itt.key_up('a')
                current_key = None
                continue

            else: 
                itt.key_up('a')
                itt.delay(0.1, is_log=False)
                itt.key_down('d')
                itt.delay(0.3, is_log=False)
                area_after_d = calculate_hsv_area(itt.capture(posi=b_area))

                if area_after_d < initial_area - 5:
                    self.log_to_gui("方向正确: D")
                    current_key = 'd'
                    while area_after_d < initial_area - 5:
                        if self.get_current_state(self.get_a_area()) != FishingState.PULL_LINE:
                            break
                        initial_area = area_after_d
                        itt.delay(0.2, is_log=False)
                        area_after_d = calculate_hsv_area(itt.capture(posi=b_area))
                    itt.key_up('d')
                    current_key = None
                    continue
                else:
                    itt.key_up('d')
                    self.log_to_gui("方向错误，重新试探")
                    continue

    @register_step("开始钓鱼")
    def fishing_loop(self):

        self.log_to_gui("开始钓鱼任务")
        itt.right_click()
        self.log_to_gui("已按下右键开始钓鱼")
        itt.delay(5, comment="等待鱼上钩")
        time.sleep(5)
        while True:
            a_area = self.get_a_area()
            state = self.get_current_state(a_area)
            self.log_to_gui(f"当前状态: {state.name}")
            if state == FishingState.NOT_FISHING or state == FishingState.UNKNOWN:
                self.log_to_gui("钓鱼结束或状态未知，任务终止")
                break

            elif state == FishingState.REEL_IN:
                self.log_to_gui("状态: 收竿, 等待")
                itt.key_down('s')
                itt.delay(0.1)
                itt.key_up('s')
                itt.delay(0.5)

            elif state == FishingState.STRIKING:
                self.log_to_gui("状态: 提竿, 按下 S")
                itt.key_down('s')
                itt.delay(0.1)
                itt.key_up('s')
                itt.delay(0.5)

            elif state == FishingState.PULL_LINE:
                self.handle_pull_line()

            elif state == FishingState.REEL_LINE:
                self.log_to_gui("状态: 收线, 点击右键")
                for _ in range(10):
                    if self.get_current_state(self.get_a_area()) != FishingState.REEL_LINE:
                        break
                    itt.right_click()
                    itt.delay(0.1, is_log=False)
                itt.delay(1)

            elif state == FishingState.SKIP:
                self.log_to_gui("状态: 跳过, 按下 F")
                itt.key_press('f')
                itt.delay(0.2)
                itt.key_press('f')
                itt.delay(0.2)
                break
        
        self.update_task_result(message="钓鱼任务完成")
        self.log_to_gui("钓鱼任务完成")


if __name__ == "__main__":
    while True:
        time.sleep(5)
        fishing_task = FishingTask()
        fishing_task.task_run()
