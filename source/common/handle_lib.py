import psutil
import win32gui, win32process
from source.common.cvars import *

global HANDLE

def get_handle():
    """获得游戏窗口句柄"""
    
    def get_hwnds_for_pid(pid):
        hwnds = []

        def callback(hwnd, hwnds):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            # 检查是否属于目标进程，且窗口是可见并且不是子窗口
            if found_pid == pid and win32gui.IsWindowVisible(hwnd) and win32gui.GetParent(hwnd) == 0:
                hwnds.append(hwnd)
            return True

        win32gui.EnumWindows(callback, hwnds)
        return hwnds
    
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == PROCESS_NAME:
            hwnds = get_hwnds_for_pid(proc.info['pid'])
            if hwnds:
                return hwnds[0]
    return 0

HANDLE = get_handle()

class handle_obj():
    def __init__(self) -> None:
        self.handle = get_handle()
    def get_handle(self):
        return self.handle
    def refresh_handle(self):
        self.handle = get_handle()

HANDLEOBJ = handle_obj()

def search_handle():
    global HANDLE
    HANDLE = get_handle()

if __name__ == '__main__':
    pass
