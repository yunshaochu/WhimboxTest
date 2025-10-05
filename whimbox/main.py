import sys
from whimbox.common.logger import logger

def init():
    """初始化应用程序环境"""
    logger.info("正在初始化应用程序环境...")
    import os
    from whimbox.config.config import GlobalConfig
    GlobalConfig()
    from whimbox.common.path_lib import SCRIPT_PATH
    if not os.path.exists(SCRIPT_PATH):
            os.makedirs(SCRIPT_PATH, exist_ok=True)
    logger.info("初始化完成")

def run_app():
    """运行主应用程序"""
    from whimbox.common.utils.utils import is_admin
    if not is_admin():
        logger.error("请用管理员权限运行")
        exit()

    from whimbox.config.config import global_config
    api_key=global_config.get("Agent", "api_key")
    if not api_key:
        logger.error("请先配置大模型的api_key")
        exit()

    from whimbox.common.handle_lib import HANDLE_OBJ
    import time
    while not HANDLE_OBJ.get_handle():
        logger.info("等待游戏启动")
        time.sleep(3)
        HANDLE_OBJ.refresh_handle()

    from whimbox.mcp_server import start_mcp_server
    from whimbox.mcp_agent import start_agent
    from whimbox.ingame_ui.ingame_ui import run_ingame_ui
    import asyncio
    import threading

    threading.Thread(target=start_mcp_server).start()
    asyncio.run(start_agent())
    run_ingame_ui()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        init()
    else:
        run_app()

if __name__ == "__main__":
    main()