from pydantic import BaseModel
from typing import Optional
import os

from source.common.path_lib import ASSETS_PATH
from source.common.logger import logger


# 自动寻路时，当距离传送点offset内，就不传送了
# 记录路线时，当起点距离传送点offset外，就不予记录
not_teleport_offset = 15


class PathInfo(BaseModel):
    name: str   # 路径名，也是导出的json文件名
    type: Optional[str] = None   # 类型：采集、捕虫、清洁、战斗、综合
    target: Optional[str] = None # 目标：素材名
    count: Optional[int] = None # 目标数量
    region: Optional[str] = None
    map: Optional[str] = None

class PathPoint(BaseModel):
    id: int
    move_mode: str          # 移动模式：行走、跳跃、飞行
    point_type: str      # 点位类型：途径点、必经点
    action: Optional[str] = None
    action_params: Optional[str] = None
    position: list[float]

class PathRecord(BaseModel):
    info: PathInfo
    points: list[PathPoint]


def get_path_json_name(target=None, type=None, count=None):
    for file in os.listdir(os.path.join(ASSETS_PATH, "paths")):
        if file.endswith(".json"):
            with open(os.path.join(ASSETS_PATH, "paths", file), "r", encoding="utf-8") as f:
                try:
                    path_record = PathRecord.model_validate_json(f.read())
                    if target and path_record.info.target == target:
                        if count and path_record.info.count >= count:
                            return file
                        elif not count:
                            return file
                    elif type and path_record.info.type == type:
                        if count and path_record.info.count >= count:
                            return file
                        elif not count:
                            return file
                except Exception as e:
                    logger.error(f"读取路径文件{file}失败: {e}")
                    continue
    return None


if __name__ == "__main__":
    print(get_path_json_name("星荧草"))