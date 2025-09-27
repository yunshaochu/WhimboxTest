import subprocess
import os
import time
import cv2
import numpy as np
import yaml
import win32gui
from pynput import keyboard


from source.common.utils.img_utils import similar_img
import mss
from source.ui.template.img_manager import LOG_NONE, ImgIcon



launch_img = ImgIcon(name="launch", path="assets/imgs/Launch/launch.png", is_bbg=True, threshold=0.999)
launching_img = ImgIcon(name="launching", path="assets/imgs/Launch/launching.png", is_bbg=True,threshold=0.999)
update_img = ImgIcon(name="update", path="assets/imgs/Launch/update.png", threshold=0.999)
update2_img = ImgIcon(name="update2", path="assets/imgs/Launch/update2.png", threshold=0.999)
# yes_img = ImgIcon(name="yes", path="assets/imgs/Launch/yes.png", threshold=0.999)
# yes3_img = ImgIcon(name="yes3", path="assets/imgs/Launch/yes3.png", threshold=0.999)
yes_mask_img = ImgIcon(name="yes_mask", path="assets/imgs/Launch/yes_mask.png", is_bbg=True, threshold=0.999)
IconUIMeiyali = ImgIcon(name="IconUIMeiyali", path="assets/imgs/Windows/UI/common/IconUIMeiyali.png",print_log=LOG_NONE, is_bbg=True,threshold=0.999)


class GameLauncher:
    def __init__(self):
        # 从YAML配置文件中读取exe_path
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'launch.yml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        self.exe_path = config.get('exe_path')
        self.capture_obj = None
        self.interrupted = False
        # 设置键盘监听器
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def on_press(self, key):
        """处理键盘按键事件"""
        try:
            # 检查是否按下了引号键
            if key.char == "'":
                print("检测到引号键按下，中断启动流程")
                self.interrupted = True
                return False  # 停止监听器
        except AttributeError:
            # 特殊键（如ctrl, alt等）会触发这个异常，我们不处理
            pass

    def is_game_running(self):
        """
        检查是否存在名为"无限暖暖"的窗口
        """
        def enum_window_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if "无限暖暖" in window_title:
                    windows.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(enum_window_callback, windows)
        return len(windows) > 0

    def is_main_menu(self):
        """
        检查是否在主菜单界面
        """
        # try:
        cap = self.capture_screen(IconUIMeiyali.bbg_posi)
        matching_rate = similar_img(cap, IconUIMeiyali.image, is_gray=False)
        result = matching_rate >= IconUIMeiyali.threshold
        print(f"是否找到主菜单: {result}")
        return result
        # except Exception as e:
        #     print(f"检查主菜单时出错: {e}")
        #     return False

    def capture_screen(self, region=None):
        """
        截图函数，默认全屏，可选指定区域

        :param region: tuple (x1, y1, x2, y2)，可选，表示要截图的矩形区域
        :return: numpy.ndarray (H, W, 3) BGR 格式图像
        """
        try:
            with mss.mss() as sct:
                if region is None:
                    # 全屏截图
                    monitor = sct.monitors[1]  # 主显示器
                else:
                    # 区域截图：转换为 mss 需要的格式
                    x1, y1, x2, y2 = map(int, region)  # 确保是 int 类型
                    monitor = {
                        "top": y1,
                        "left": x1,
                        "width": x2 - x1,
                        "height": y2 - y1
                    }

                screenshot = sct.grab(monitor)
                img = np.array(screenshot)

                # 转换为BGR格式（OpenCV使用BGR）
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                return img

        except Exception as e:
            print(f"截图时出错: {e}")
            # 出错时返回一个空图像（尺寸根据是否区域截图决定）
            if region is None:
                return np.zeros((1080, 1920, 3), dtype=np.uint8)
            else:
                x1, y1, x2, y2 = map(int, region)
                h, w = y2 - y1, x2 - x1
                return np.zeros((h, w, 3), dtype=np.uint8)

    def find_image_and_click(self, img_icon, max_attempts=30):
        """
        查找并点击图像
        :param img_icon: ImgIcon对象
        :param max_attempts: 最大尝试次数
        """
        attempts = 0
        
        while attempts < max_attempts:
            # 检查是否被中断
            if self.interrupted:
                print("启动流程已被中断")
                return False
                
            # 截图
            if img_icon.is_bbg:
                screenshot = self.capture_screen(img_icon.bbg_posi)
            else:
                screenshot = self.capture_screen()

            # 在截图中查找图像
            matching_rate, max_loc = similar_img(screenshot, img_icon.image, True, ret_mode=3)
            
            if matching_rate >= img_icon.threshold:
                print(f"找到图像 {img_icon.name}，匹配度: {matching_rate}")
                # 计算点击位置
                click_x = max_loc[0] + img_icon.cap_posi[0] + img_icon.image.shape[1] // 2
                click_y = max_loc[1] + img_icon.cap_posi[1] + img_icon.image.shape[0] // 2
                
                # 点击位置
                self.click_coordinate(click_x, click_y)
                print(f"点击了 {img_icon.name} 在位置 ({click_x}, {click_y})")
                return True
                
            time.sleep(0.5)
            attempts += 1
            
        print(f"未能找到图像 {img_icon.name}")
        return False

    def find_any_image(self, img_icons, max_attempts=30):
        """
        查找任意一个图像
        :param img_icons: ImgIcon对象列表
        :param max_attempts: 最大尝试次数
        """
        attempts = 0
        
        while attempts < max_attempts:
            # 检查是否被中断
            if self.interrupted:
                print("启动流程已被中断")
                return None
                
            # 截图（为所有图像使用同一张截图以提高效率）
            screenshots = {}
            for img_icon in img_icons:
                if img_icon.is_bbg:
                    key = tuple(img_icon.bbg_posi)
                    if key not in screenshots:
                        screenshots[key] = self.capture_screen(img_icon.bbg_posi)
                else:
                    # 使用全屏截图
                    if 'full' not in screenshots:
                        screenshots['full'] = self.capture_screen()
            
            results = {}
            for img_icon in img_icons:
                if img_icon.is_bbg:
                    screenshot = screenshots[tuple(img_icon.bbg_posi)]
                else:
                    screenshot = screenshots['full']
                    
                matching_rate = similar_img(screenshot, img_icon.image)
                results[img_icon] = matching_rate

            # 检查是否有匹配的图像
            for img_icon, matching_rate in results.items():
                if matching_rate >= img_icon.threshold:
                    print(f"找到图像 {img_icon.name}，匹配度: {matching_rate}")
                    return img_icon
                    
            time.sleep(0.5)
            attempts += 1
            
        print(f"未能找到任何图像")
        return None

    def click_coordinate(self, x, y):
        """
        点击指定坐标
        :param x: X坐标
        :param y: Y坐标
        """
        try:
            # 使用win32api直接点击，不依赖itt, 不然会找不到游戏窗口而报错
            import win32api, win32con
            win32api.SetCursorPos((int(x), int(y)))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, int(x), int(y), 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, int(x), int(y), 0, 0)
        except Exception as e:
            print(f"点击坐标时出错: {e}")

    def launch_game(self):
        """
        启动游戏程序并开始检测图片。
        :param exe_path: 游戏启动器路径
        """
        print("开始启动游戏，按引号键(')可中断启动流程")
        if self.is_game_running():
            print("检测到游戏窗口已存在，跳过启动")
            return
            
        exe_path = self.exe_path

        if os.path.exists(exe_path):
            try:
                subprocess.run([exe_path])
                print("程序已启动，开始检测图片...")
            except subprocess.CalledProcessError as e:
                print(f"启动程序时出错: {e}")
            except Exception as e:
                print(f"发生未知错误: {e}")
        else:
            print("指定路径的文件不存在，请检查路径是否正确。")
            return

        time.sleep(5)

        # 等待游戏启动完成
        start_time = time.time()

        wait = True
        while True:
            # 检查是否被中断
            if self.interrupted:
                print("启动流程已被中断")
                break
                
            # 检查是否超时（20分钟）
            if time.time() - start_time > 1200:
                raise TimeoutError("启动游戏超时，超过20分钟未进入主菜单")

            # 查找并处理可能出现的对话框
            # found_img = self.find_any_image([ launch_img, launching_img, update_img, yes3_img, yes_img, update2_img], max_attempts=1)

            found_img = self.find_any_image([ launch_img, launching_img, update_img, yes_mask_img, update2_img], max_attempts=1)

            
            time.sleep(0.3)

            if self.interrupted:
                print("启动流程已被中断")
                break

            if found_img and found_img is not launching_img:
                self.find_image_and_click(found_img)

            if found_img is launching_img:
                wait = False
                self.click_coordinate(900, 800)

            if found_img is update_img or found_img is update2_img:
                wait = True

            if wait:
                continue

            if self.is_main_menu():
                print("成功进入主菜单")
                break
            print("等待游戏启动...")

            self.click_coordinate(900, 800)

        print("游戏启动完成")

if __name__ == "__main__":
    launcher = GameLauncher()
    launcher.launch_game()