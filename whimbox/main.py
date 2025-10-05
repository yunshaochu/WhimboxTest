from whimbox.common.utils.utils import is_admin
from whimbox.common.logger import logger
if not is_admin():
    logger.error("请用管理员权限运行")
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

def main():
    threading.Thread(target=start_mcp_server).start()
    asyncio.run(start_agent())
    run_ingame_ui()