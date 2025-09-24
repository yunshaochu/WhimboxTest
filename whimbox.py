from source.common.utils.utils import is_admin
from source.common.logger import logger
if not is_admin():
    logger.error("请用管理员权限运行")
    exit()

from source.common.handle_lib import HANDLE_OBJ
if not HANDLE_OBJ.get_handle():
    logger.error("请先启动游戏")
    exit()

from source.mcp_server import start_mcp_server
from source.mcp_agent import start_agent
from source.ingame_ui.ingame_ui import run_ingame_ui

import asyncio
import threading

def main():
    threading.Thread(target=start_mcp_server).start()
    asyncio.run(start_agent())
    HANDLE_OBJ.set_foreground()
    run_ingame_ui()


if __name__ == '__main__':
    main()