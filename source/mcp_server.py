import source.task.daily_task as daily_task
from source.task.navigation_task.common import get_path_json_name
from source.task.navigation_task.auto_path_task import AutoPathTask
from source.task.navigation_task.record_path_task import RecordPathTask
from source.common.path_lib import ASSETS_PATH

from fastmcp import FastMCP
import os

mcp = FastMCP('whimbox_server')


@mcp.tool()
async def jihua_task() -> dict:
    """
    素材激化：消耗活跃能量，用大世界材料换取噗灵、丝线、泡泡

    Returns:
        dict: 包含操作状态的字典，包含status和message字段
    """
    jihua_task = daily_task.JihuaTask()
    task_result = jihua_task.task_run()
    return task_result.to_dict()


@mcp.tool()
async def dig_task() -> dict:
    """
    美鸭梨挖掘：获得少量大世界材料

    Returns:
        dict: 包含操作状态的字典，包含status和message字段
    """
    dig_task = daily_task.DigTask()
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
async def navigation_task(target_item) -> dict:
    """
    自动跑图，自动寻路并进行采集、捕虫、钓鱼、战斗等操作

    Args:
        target_item: 要获取的素材名

    Returns:
        dict: 包含操作状态的字典，包含status和message字段
    """
    path_json_name = get_path_json_name(target_item)
    if path_json_name is None:
        return {
            "status": "error",
            "message": f"暂时没有{target_item}的路线"
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
            "status": "error",
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
        "status": "success",
        "message": f"已打开路线编辑网站，请在浏览器中编辑路径文件"
    }

def start_mcp_server():
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=2333,
    )
    