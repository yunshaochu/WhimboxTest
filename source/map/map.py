from source.common import timer_module
from source.map.detection.cvars import MOVE_SPEED
from source.ui.ui import ui_control
from source.ui.ui_assets import *
from source.ui.page_assets import *
from source.interaction.interaction_core import itt
from source.map.data.nikki_teleporter import DICT_TELEPORTER
from source.map.detection.bigmap import BigMap
from source.map.detection.minimap import MiniMap
from source.map.detection.utils import trans_region_name_to_map_name
from source.map.convert import *
from source.common.logger import logger
from source.common.utils.posi_utils import *
from source.common.errors import BigMapTPError
from source.common.utils.ui_utils import *

import threading
import time
import typing as t


class Map(MiniMap, BigMap):

    def __init__(self):
        MiniMap.__init__(self)
        BigMap.__init__(self)

        # Set bigmap tp arguments
        self.MAP_POSI2MOVE_POSI_RATE = 0.5  # 移动距离与力度的比例
        self.BIGMAP_TP_OFFSET = 20  # 距离目标小于该误差则停止
        self.BIGMAP_MOVE_MAX = 130  # 最大移动力度
        self.TP_RANGE = 200  # 在该像素范围内可tp
        self.MINIMAP_UPDATE_LIMIT = 0.1  # minimap更新最短时间
        self.MINIMAP_ERROR_BASE_LIMIT = 20  # minimap基本更新误差

        self.smallmap_upd_timer = timer_module.Timer(10)
        self.small_map_init_flag = False
        self.lock = threading.Lock()
        self.check_bigmap_timer = timer_module.Timer(5)
        self.last_valid_position = [0, 0]
        self.history_position_list = []
        self.region_name = None
        self.map_name = None
        

    def _upd_smallmap(self) -> None:
        if itt.get_img_existence(IconUIMeiyali):
            self.update_position(itt.capture())


    def _is_reset_position(self, curr_posi, threshold=0.8):
        """如果历史点位种有threshold％偏移超过150px，则返回True。

        Args:
            curr_posi (_type_): _description_
            threshold (float, optional): _description_. Defaults to 0.8.

        Returns:
            _type_: _description_
        """
        if len(self.history_position_list) >= 20:
            over_times = 0
            for i in self.history_position_list:
                if euclidean_distance(i, curr_posi) >= 150:
                    over_times += 1
            return over_times / 20 > threshold
        return False

    def get_position(self, is_verify_position=False, use_cache = False):
        """get current character position

        Returns:
            list: px format
        """
        if use_cache:
            return self.position

        if not self.small_map_init_flag:
            self.reinit_smallmap()
            self.small_map_init_flag = True
            
        self._upd_smallmap()
        self.history_position_list.append(self.position)
        # 由于minimap的update_position方法种已经有校验了，所以这里一般不校验
        if is_verify_position:
            if self._is_reset_position(self.position):
                self.history_position_list = []
            else:
                last_dist = euclidean_distance(self.last_valid_position, self.position)
                error_limit = self.MINIMAP_ERROR_BASE_LIMIT + self.smallmap_upd_timer.get_diff_time() * MOVE_SPEED
                if last_dist > error_limit:
                    logger.warning(
                        f"migration of position {round(last_dist, 2)} over limit {round(error_limit, 2)}, give up position")
                    self.minimap_print_log()
                    return self.last_valid_position

        self.smallmap_upd_timer.reset()
        r_posi = self.position
        self.last_valid_position = r_posi
        if len(self.history_position_list) > 20:
            self.history_position_list.pop(0)
        return list(r_posi)


    def update_region_and_map_name(self, use_cache=False) -> str:
        if use_cache and self.region_name is not None and self.map_name is not None:
            return self.region_name, self.map_name
        else:
            hsv_lower = np.array([0, 0, 0])  
            hsv_upper = np.array([180, 255, 180])   # hsv阈值处理，排除地图背景图案和文字的干扰
            self.region_name= itt.ocr_single_line(AreaBigMapRegionName, padding=50, hsv_limit=(hsv_lower, hsv_upper))
            self.map_name = trans_region_name_to_map_name(self.region_name)
            return self.region_name, self.map_name


    def reinit_smallmap(self) -> None:
        ui_control.ui_goto(page_bigmap)
        self.update_region_and_map_name()
        posi = self.get_bigmap_posi()
        logger.info(f"init_position:{posi}")
        self.init_position(tuple(map(int, list(posi))))
        ui_control.ui_goto(page_main)
        self.small_map_init_flag = True
        self.last_valid_position = self.position
        self.smallmap_upd_timer.reset()

    def get_smallmap_from_teleporter(self, area=None):
        if area == None:
            area = ['Inazuma', "Liyue", "Mondstadt"]
        tpers_dict = []
        rlist = []
        rd = []
        added = []
        for md in [60]:
            logger.info(f"d: {md}")
            for i in DICT_TELEPORTER:
                tper = DICT_TELEPORTER[i]
                if not tper.region in area:
                    continue

                # logger.info(f"init_position:{tper.position}")
                self.init_position(tper.position)
                self.get_position()
                d = euclidean_distance(self.get_position(),
                                       self.convert_GIMAP_to_cvAutoTrack(tper.position))
                if d <= md:
                    if tper in added:
                        continue
                    tpers_dict.append(
                        {
                            'tper': tper,
                            'd': d
                        }
                    )
                    # logger.info(f"id {len(rlist)-1} position {tper.position} {tper.name} {tper.region}, d={d}")
                    added.append(tper)
        tpers_dict.sort(key=lambda x: x['d'])
        return [i['tper'] for i in tpers_dict], [i['d'] for i in tpers_dict]
        # self.init_position(tuple(list(map(int,max_position))))
        # logger.info(f"init_smallmap_from_teleporter:{max_n} {max_position} {max_tper.name}")

    def while_until_no_excessive_error(self) -> None:
        self.reinit_smallmap()

    def get_direction(self) -> float:
        self.update_direction(itt.capture())
        return self.direction

    def get_rotation(self) -> float:
        pt = time.time()
        self.update_rotation(itt.capture())
        if time.time() - pt > 0.1:
            logger.info(f"get_rotation spent too long: {time.time() - pt}")
        return self.rotation

    def maximize_bigmap_scale(self) -> None:
        # todo：原地tp，会导致ButtonBigMapZoom被弹出的传送菜单遮挡，无法继续
        ui_control.ensure_page(page_bigmap)
        while not itt.get_img_existence(IconBigMapMaxScale):
            itt.appear_then_click(ButtonBigMapZoom)
            time.sleep(0.5)

    def get_bigmap_posi(self, is_upd=True) -> t.Tuple[float, float]:
        self.maximize_bigmap_scale()
        if is_upd:
            self.update_bigmap(itt.capture())
        logger.debug(f"bigmap px posi: {self.bigmap_position}")
        return self.bigmap_position

    def _move_bigmap(self, target_posi, float_posi=0, force_center=False, csf=lambda: False) -> list:
        """move bigmap center to target position

        Args:
            target_posi (_type_): png map上的目标坐标 
            float_posi (int, optional): 如果点到了什么东东导致移动失败，自动增加该值. Defaults to 0.

        Returns:
            _type_: _description_
        """

        """需要处理的异常：

        1. 点击到某个东西弹出右侧弹框
        2. 点击到一坨按键弹出一坨东西
        
        警告：此函数为内部函数，不要在外部调用。如果一定要调用应先设置地图缩放。
        
        """
        screen_center_x = 1920 / 2
        screen_center_y = 1080 / 2

        if csf():
            return

        itt.move_to([screen_center_x + float_posi, screen_center_y + float_posi])  # screen center
        itt.left_down()

        # 瞎几把拖几下地图，防止游戏没反应过来
        for i in range(5):
            itt.move_to([10, 10], relative=True)
            if i % 2 == 0:
                itt.left_down()
        for i in range(5):
            itt.move_to([-10, -10], relative=True)
            if i % 2 == 0:
                itt.left_down()

        curr_posi = self.get_bigmap_posi()
        dx = min((curr_posi[0] - target_posi[0]) * self.MAP_POSI2MOVE_POSI_RATE, self.BIGMAP_MOVE_MAX)
        dx = max(dx, -self.BIGMAP_MOVE_MAX)
        dy = min((curr_posi[1] - target_posi[1]) * self.MAP_POSI2MOVE_POSI_RATE, self.BIGMAP_MOVE_MAX)
        dy = max(dy, -self.BIGMAP_MOVE_MAX)

        logger.debug(f"curr: {curr_posi} target: {target_posi}")
        logger.debug(f"_move_bigmap: {dx} {dy}")

        itt.move_to([dx, dy], relative=True)
        itt.delay(0.2, comment="waiting bigmap move")
        itt.left_up()

        after_move_posi = self.get_bigmap_posi()
        if not force_center:
            if euclidean_distance(
                convert_PngMapPx_to_InGameMapPx(after_move_posi, self.map_name), 
                convert_PngMapPx_to_InGameMapPx(target_posi, self.map_name)
                ) <= self.TP_RANGE:
                return list(
                    convert_PngMapPx_to_InGameMapPx(target_posi, self.map_name)
                    - convert_PngMapPx_to_InGameMapPx(after_move_posi, self.map_name)
                    + np.array([screen_center_x, screen_center_y]))

        if euclidean_distance(after_move_posi, target_posi) <= self.BIGMAP_TP_OFFSET:
            return list([screen_center_x, screen_center_y])  # screen center
        else:
            if euclidean_distance(after_move_posi, curr_posi) <= self.BIGMAP_TP_OFFSET:
                return self._move_bigmap(target_posi=target_posi, float_posi=float_posi + 45)
            else:
                return self._move_bigmap(target_posi=target_posi)

    def find_closest_teleporter(self, posi: list, map_name: str):
        """
        return closest teleporter position: 
        
        input:  png map position;
        return: png map position.
        """
        min_dist = 99999
        min_teleporter = None
        for checkpoint in DICT_TELEPORTER[map_name]:
            if checkpoint.province in PROVINCE_NAMES:
                cp_posi = checkpoint.position
                dist = euclidean_distance(posi, cp_posi)
                if dist < min_dist:
                    min_teleporter = checkpoint
                    min_dist = dist
        return min_teleporter

    def _switch_to_area(self, tp_province, tp_region):

        def click_box(box, parent_area):
            offset = (parent_area.position[0], parent_area.position[1])
            center = area_center(box)
            center = (center[0] + offset[0], center[1] + offset[1])
            itt.move_and_click(center)

        # 判断当前区域是否是目标区域
        current_region, _ = self.update_region_and_map_name()
        if current_region != tp_region:
            # 不是目标区域，就进行区域选择
            itt.move_and_click(AreaBigMapRegionName.center_position())
            time.sleep(0.5)
            text_box_dict = itt.ocr_and_detect_posi(AreaBigMapRegionSelect)
            if tp_province == "星海":
                box = text_box_dict["星海"]
                click_box(box, AreaBigMapRegionSelect)
                itt.wait_until_stable()
                self.update_region_and_map_name()
                return True
            elif tp_province == "心愿原野":
                # 如果识别出“纪念山地”，说明心愿原野下拉框已展开
                if not "纪念山地" in text_box_dict:
                    box = text_box_dict["心愿原野"]
                    click_box(box, AreaBigMapRegionSelect)
                    time.sleep(0.5)
                if scroll_find_click(AreaBigMapRegionSelect, tp_region):
                    itt.wait_until_stable()
                    self.update_region_and_map_name()
                    return True
                # scroll_times = 2
                # while scroll_times > 0:
                #     text_box_dict = itt.ocr_and_detect_posi(AreaBigMapRegionSelect)
                #     if tp_region in text_box_dict:
                #         click_box(text_box_dict[tp_region], AreaBigMapRegionSelect)
                #         itt.wait_until_stable()
                #         self.update_region_and_map_name()
                #         return True
                #     itt.move_to(AreaBigMapRegionSelect.center_position())
                #     itt.middle_scroll(-15)
                #     scroll_times -= 1
                #     time.sleep(0.5)
            return False
        else:
            return True

    def bigmap_tp(self, posi: list, map_name: str, csf=lambda: False) -> t.Tuple[float, float]:
        """传送到指定坐标。

        Args:
            posi (list)
            csf (_type_, optional): checkup stop func. Defaults to lambda:False.

        Returns:
            TianLiPosition: _description_
        """
        logger.debug(f'bigmap tp to: {posi}')
        ui_control.ensure_page(page_bigmap)
        target_teleporter = self.find_closest_teleporter(posi, map_name)
        tp_posi = target_teleporter.position
        tp_province = target_teleporter.province
        tp_region = target_teleporter.region

        ui_control.ensure_page(page_bigmap)
        self.maximize_bigmap_scale()
        switch_success = self._switch_to_area(tp_province, tp_region)
        if not switch_success:
            logger.error(f"switch to {tp_province} {tp_region} failed")
            raise Exception(f"switch to {tp_province} {tp_region} failed")

        click_posi = self._move_bigmap(tp_posi, csf=csf)
        itt.move_and_click(click_posi)
        itt.wait_until_stable()
        if not itt.appear_then_click(ButtonBigMapTeleport):
            # 传送点和其他图标重合的情况下，如果点击传送点，会弹出选择菜单
            hsv_lower = np.array([0, 0, 220])  
            hsv_upper = np.array([180, 15, 255])   # hsv阈值处理，排除地图背景图案和文字的干扰
            if scroll_find_click(AreaBigMapTeleporterSelect, target_teleporter.name, hsv_limit=(hsv_lower, hsv_upper)):
                itt.wait_until_stable()
                if not itt.appear_then_click(ButtonBigMapTeleport):
                    raise BigMapTPError("bigmap tp failed")
            else:
                raise BigMapTPError("bigmap tp failed")

        # 等待传送完成
        while not (ui_control.get_page() == page_main):
            time.sleep(0.5)

        self.init_position(tp_posi)

        return tp_posi

nikki_map = Map()
logger.info(f"nikki map object created")

if __name__ == '__main__':
    # 花愿镇
    # nikki_map.bigmap_tp([ 6425.3,4381.0], MAP_NAME_MIRALAND)
    # 传送到星海无界枢纽
    # nikki_map.bigmap_tp([1696, 2029], MAP_NAME_STARSEA)
    # 传送到星海海滩
    # nikki_map.bigmap_tp([3341, 2352], MAP_NAME_STARSEA)

    # res = itt.ocr_and_detect_posi(AreaBigMapRegionSelect)
    # print(res)
    
    CV_DEBUG_MODE = True
    nikki_map.bigmap_tp([6188, 5446.5], MAP_NAME_MIRALAND)
