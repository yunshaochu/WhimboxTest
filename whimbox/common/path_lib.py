import os
import win32api, win32con
import configparser

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# # 判断是否在开发模式（存在 dev_mode 文件）
# _is_dev_mode = os.path.exists(os.path.join(ROOT_PATH, 'dev_mode'))

# if _is_dev_mode:
#     # 开发模式：使用源码路径
#     print("开发模式：使用源码路径\n")
#     ASSETS_PATH = os.path.join(ROOT_PATH, 'assets')
#     CONFIG_PATH = os.path.join(ROOT_PATH, 'configs')
#     LOG_PATH = os.path.join(ROOT_PATH, 'logs')
# else:
#     # 打包模式：使用包内资源
#     print("打包模式：使用包内资源\n")
#     from importlib.resources import files
#     ASSETS_PATH = str(files('assets'))
#     CONFIG_PATH = os.path.join(os.getcwd(), "configs")
#     LOG_PATH = os.path.join(os.getcwd(), "logs")

ASSETS_PATH = os.path.join(ROOT_PATH, 'assets')
CONFIG_PATH = os.path.join(os.getcwd(), 'configs')
LOG_PATH = os.path.join(os.getcwd(), 'logs')
SCRIPT_PATH = os.path.join(os.getcwd(), 'scripts')

def find_game_launcher_folder():
    # HKEY_CURRENT_USER\Software\InfinityNikki Launcher
    path = ""
    key = 'Software\\InfinityNikki Launcher'
    try:
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, key, 0, win32con.KEY_READ)
        path, _ = win32api.RegQueryValueEx(key, "")  # 读取默认值
        win32api.RegCloseKey(key)
    except Exception as e:
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
            return ""


if __name__ == "__main__":
    print(find_game_launcher_folder())
    print(find_game_folder())

