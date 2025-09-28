import os, sys
import win32api, win32con
import logging
import configparser

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT_PATH)
SOURCE_PATH = ROOT_PATH + '\\source'
ASSETS_PATH = ROOT_PATH + '\\assets'
if sys.path[0] != ROOT_PATH:
    sys.path.insert(0, ROOT_PATH)
if sys.path[1] != SOURCE_PATH:
    sys.path.insert(1, SOURCE_PATH)

CONFIG_PATH = os.path.join(ROOT_PATH,"config")


def find_game_launcher_folder():
    # HKEY_CURRENT_USER\Software\InfinityNikki Launcher
    path = ""
    key = 'Software\\InfinityNikki Launcher'
    try:
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, key, 0, win32con.KEY_READ)
        path, _ = win32api.RegQueryValueEx(key, "")  # 读取默认值
        win32api.RegCloseKey(key)
    except Exception as e:
        logging.error(f"find launcher folder failed: {e}")
        path = ""
    
    return path

def find_game_folder():
    user_home = os.path.expanduser('~')
    config_path = os.path.join(user_home, 'AppData', 'Local', 'InfinityNikki Launcher', 'config.ini')
    if not os.path.exists(config_path):
        return ""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = configparser.ConfigParser()
        config.read_file(f)
        try:
            return config['Download']['gameDir']
        except (KeyError, configparser.NoSectionError):
            logging.error("find game folder failed")
            return ""


if __name__ == "__main__":
    print(find_game_launcher_folder())
    print(find_game_folder())

