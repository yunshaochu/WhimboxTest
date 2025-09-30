import source.task.daily_task as daily_task
from source.task.navigation_task.common import get_path_json_name
from source.task.navigation_task.auto_path_task import AutoPathTask
from source.task.navigation_task.record_path_task import RecordPathTask
from source.task.photo_task.daily_photo_task import DailyPhotoTask
from source.task.task_template import STATE_TYPE_SUCCESS, STATE_TYPE_ERROR
from source.common.path_lib import ASSETS_PATH

from fastmcp import FastMCP
import os

mcp = FastMCP('whimbox_server')


@mcp.tool()
async def jihua_task(target_material=None, cost_material=None) -> dict:
    """
    素材激化：消耗活跃能量，用大世界材料换取噗灵、丝线、闪亮泡泡

    Args:
        target_material: 可选，用于兑换的材料名，只支持噗灵、丝线、闪亮泡泡。如果不输入，会自动读取配置文件
        cost_material: 可选，用于消耗材料名。如果不输入，会自动读取配置文件

    Returns:
        dict: 包含操作状态的字典，包含status和message字段
    """
    jihua_task = daily_task.JihuaTask(target_material, cost_material)
    task_result = jihua_task.task_run()
    return task_result.to_dict()


@mcp.tool()
async def bless_task(level_name=None) -> dict:
    """
    消耗活跃能量，获取祝福闪光

    Args:
        level_name: 可选，要挑战的祝福闪光幻境的关卡名，如果不输入，会自动读取配置文件

    Returns:
        dict: 包含操作状态的字典，包含status和message字段

    Example:
        (level_name=巨蛇遗迹试炼)
    """
    bless_task = daily_task.BlessTask(level_name)
    task_result = bless_task.task_run()
    return task_result.to_dict()


@mcp.tool()
async def dig_task(target_item_list=None) -> dict:
    """
    美鸭梨挖掘，只有当明确说明“挖掘”或“美鸭梨挖掘”时才能调用这个工具

    Args:
        target_item_list: 可选，要挖掘的材料名列表，如果不输入，会自动读取配置文件

    Returns:
        dict: 包含操作状态的字典，包含status和message字段
    """
    dig_task = daily_task.DigTask(target_item_list)
    task_result = dig_task.task_run()
    return task_result.to_dict()

@mcp.tool()
async def zhaoxi_task() -> dict:
    """
    检查每日任务（朝夕心愿）的进度

    Returns:
        dict: 包含操作状态的字典，包含status和message字段
    """
    zhaoxi_task = daily_task.ZhaoxiTask()
    task_result = zhaoxi_task.task_run()
    return task_result.to_dict()


@mcp.tool()
async def navigation_task(target=None, type=None, count=None) -> dict:
    """
    指定素材名，或素材获取方法，进行获取。可以同时指定最少要获取的数量

    Args:
        target: 可选，要获取的素材名
        type: 可选，素材获取方法，只能输入“采集”、“捕虫”、“钓鱼”、“清洁”
        count: 可选，最少要获取的素材数量

    Returns:
        dict: 包含操作状态的字典，包含status和message字段

    Example:
        (target=星荧草),
        (type=采集)
        (target=发卡蚱蜢, count=1)
        (type=钓鱼, count=3)
    """
    path_json_name = get_path_json_name(target, type, count)
    if path_json_name is None:
        return {
            "status": STATE_TYPE_ERROR,
            "message": f"没有符合要求的跑图路线"
        }
    else:
        task = AutoPathTask(path_json_name)
        task_result = task.task_run()
        return task_result.to_dict()

@mcp.tool()
async def load_path(path_name: str) -> dict:
    """
    加载并测试指定的跑图路径文件

    Args:
        path_name: 路径文件名

    Returns:
        dict: 包含操作状态的字典，包含status和message字段
    """
    path_json_name = f'{path_name}.json'
    if os.path.exists(os.path.join(ASSETS_PATH, "paths", path_json_name)):
        task = AutoPathTask(path_json_name)
        task_result = task.task_run()
        return task_result.to_dict()
    else:
        return {
            "status": STATE_TYPE_ERROR,
            "message": f"路径文件{path_json_name}不存在"
        }

@mcp.tool()
async def record_path() -> dict:
    """
    记录跑图路线

    Returns:
        dict: 包含操作状态的字典，包含status和message字段
    """
    task = RecordPathTask()
    task_result = task.task_run()
    return task_result.to_dict()

@mcp.tool()
async def edit_path() -> dict:
    """
    用浏览器前往路线编辑网站，编辑指定的跑图路径文件
    
    Returns:
        dict: 包含操作状态的字典，包含status和message字段
    """
    import webbrowser
    webbrowser.open(f"https://nikkigallery.vip/autotools/pathcheck")
    return {
        "status": STATE_TYPE_SUCCESS,
        "message": f"已打开路线编辑网站，请在浏览器中编辑路径文件"
    }

@mcp.tool()
async def daily_photo_task() -> dict:
    """
    简单拍照，用于完成每日任务

    Returns:
        dict: 包含操作状态的字典，包含status和message字段
    """
    daily_photo_task = DailyPhotoTask()
    task_result = daily_photo_task.task_run()
    return task_result.to_dict()

def start_mcp_server():
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=2333,
    )
    