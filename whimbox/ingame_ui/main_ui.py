import win32gui
import win32con
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pynput import keyboard
import sys

from whimbox.common.handle_lib import HANDLE_OBJ
from whimbox.common.logger import logger
from whimbox.common.utils.utils import get_active_window_process_name
from whimbox.common.cvars import PROCESS_NAME

from whimbox.ingame_ui.components import CollapsedChatWidget, SettingsDialog, ChatView

update_time = 500  # ui更新间隔，ms

class IngameUI(QWidget):
    def __init__(self):
        super().__init__()
        
        # 状态管理
        self.is_expanded = False
        self.current_view = "chat"  # "chat" 或 "function"
        
        # UI组件
        self.collapsed_widget = None
        self.expanded_widget = None
        self.chat_view = None  # ChatView组件
        self.function_view_widget = None
        self.chat_tab = None
        self.function_tab = None
        self.settings_dialog = None
        
        # 初始化UI
        self.init_ui()
        
        # 计时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui_position)
        self.timer.start(update_time)

        # 窗口设置
        self.setWindowTitle("奇想盒")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        hwnd = int(self.winId())
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_TRANSPARENT)
        self.last_bbox = 0
        
        # 键盘监听
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.daemon = True
        self.listener.start()

    def on_key_press(self, key):
        if key == keyboard.KeyCode.from_char('/'):
            QTimer.singleShot(0, self.on_slash_pressed)
        elif key == keyboard.Key.esc:
            QTimer.singleShot(0, self.on_esc_pressed)
    
    
    def init_ui(self):
        """初始化UI组件"""
        # 创建收缩状态组件
        self.collapsed_widget = CollapsedChatWidget(self)
        self.collapsed_widget.clicked.connect(self.show_expanded)
        
        # 创建展开状态组件
        self.create_expanded_widget()
        
        # 默认显示收缩状态
        self.show_collapsed()
    
    def create_expanded_widget(self):
        """创建展开状态的聊天界面"""
        self.expanded_widget = QWidget(self)
        self.expanded_widget.setFixedSize(500, 600)
        self.expanded_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 120);
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        # 主布局
        layout = QVBoxLayout(self.expanded_widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # 标题栏
        title_layout = QHBoxLayout()
        title_label = QLabel("📦奇想盒")
        title_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                font-size: 14px;
                font-weight: bold; 
                border: none; 
            }
        """)
        
        settings_button = QPushButton("⚙️")
        settings_button.setFixedSize(25, 25)
        settings_button.clicked.connect(self.open_settings)
        settings_button.setStyleSheet("""
            QPushButton {
                background-color: #E3F2FD;
                border: 2px solid #2196F3;
                font-size: 12px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        minimize_button = QPushButton("➖")
        minimize_button.setFixedSize(25, 25)
        minimize_button.clicked.connect(self.collapse_chat)
        minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #FFF9C4;
                border: 2px solid #FBC02D;
                font-size: 12px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #F9A825;
            }
        """)

        close_button = QPushButton("❌")
        close_button.setFixedSize(25, 25)
        close_button.clicked.connect(self.close_application)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #FFEBEE;
                border: 2px solid #F44336;
                font-size: 12px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(settings_button)
        title_layout.addWidget(minimize_button)
        title_layout.addWidget(close_button)
        
        # Tab导航栏
        tab_layout = QHBoxLayout()
        tab_layout.setSpacing(4)
        tab_layout.setContentsMargins(0, 4, 0, 4)
        
        self.chat_tab = QPushButton("💬 聊天")
        self.chat_tab.setFixedHeight(35)
        self.chat_tab.clicked.connect(lambda: self.switch_to_tab("chat"))
        
        self.function_tab = QPushButton("⚡ 功能")
        self.function_tab.setFixedHeight(35)
        self.function_tab.clicked.connect(lambda: self.switch_to_tab("function"))
        
        # Tab样式
        self.update_tab_styles()
        
        tab_layout.addWidget(self.chat_tab)
        tab_layout.addWidget(self.function_tab)
        
        # 创建聊天视图组件
        self.chat_view = ChatView(self.expanded_widget)
        # 连接焦点管理信号
        self.chat_view.request_focus.connect(self.acquire_focus)
        self.chat_view.release_focus.connect(self.give_back_focus)
        
        # 创建功能视图
        self.function_view_widget = self.create_function_view()
        
        # 组装布局
        layout.addLayout(title_layout)
        layout.addLayout(tab_layout)
        layout.addWidget(self.chat_view, 1)
        layout.addWidget(self.function_view_widget, 1)
        
        # 默认显示聊天视图
        self.function_view_widget.hide()
    
    def create_function_view(self):
        """创建功能视图"""
        function_view = QWidget()
        function_view.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        
        function_layout = QVBoxLayout(function_view)
        function_layout.setContentsMargins(0, 0, 0, 0)
        function_layout.setSpacing(0)
        
        # 功能内容区域
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                background-color: rgba(240, 240, 240, 150);
            }
        """)
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignCenter)
        
        # 添加一个占位标签
        placeholder_label = QLabel("⚡ 功能面板\n\n敬请期待...")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: #757575;
                font-size: 18px;
                border: none;
            }
        """)
        
        content_layout.addWidget(placeholder_label)
        function_layout.addWidget(content_widget)
        
        return function_view
    
    
    def show_collapsed(self):
        """显示收缩状态"""
        self.is_expanded = False
        if self.expanded_widget:
            self.expanded_widget.hide()
        if self.collapsed_widget:
            self.collapsed_widget.show()
        self.setGeometry(0, 0, 128, 128)  # 设置小窗口大小
    
    def show_expanded(self):
        """显示展开状态"""
        self.is_expanded = True
        if self.collapsed_widget:
            self.collapsed_widget.hide()
        if self.expanded_widget:
            self.expanded_widget.show()
        self.setGeometry(0, 0, 520, 620)  # 设置大窗口大小

    def expand_chat(self):
        """展开聊天界面"""
        logger.info("Expanding chat interface")
        self.show_expanded()
        self.position_window()
        self.acquire_focus()
        
        # 延迟设置焦点，确保窗口完全展开
        QTimer.singleShot(100, lambda: self.chat_view.set_focus_to_input() if self.chat_view else None)
        
        # 添加欢迎消息（仅在首次展开时）
        if self.chat_view and not self.chat_view.has_messages():
            self.chat_view.add_message("👋 您好！我是奇想盒📦，请告诉我你想做什么？。", 'ai')
    
    def collapse_chat(self):
        """收缩聊天界面"""
        logger.info("Collapsing chat interface")
        self.show_collapsed()
        self.position_window()
        self.give_back_focus()
    
    def close_application(self):
        """关闭应用程序"""
        # 创建确认对话框
        reply = QMessageBox.question(
            self,
            '确认关闭',
            '确定要关闭奇想盒吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info("User confirmed - closing whimbox")
            sys.exit(0)
    
    def switch_to_tab(self, tab_name: str):
        """切换到指定的tab"""
        if tab_name == "chat":
            self.chat_view.show()
            self.function_view_widget.hide()
            self.current_view = "chat"
            logger.info("Switched to chat tab")
        else:  # function
            self.chat_view.hide()
            self.function_view_widget.show()
            self.current_view = "function"
            logger.info("Switched to function tab")
        
        # 更新tab样式
        self.update_tab_styles()
    
    def update_tab_styles(self):
        """更新tab按钮的样式"""
        active_style = """
            QPushButton {
                background-color: rgba(33, 150, 243, 200);
                color: white;
                border: none;
                border-bottom: 3px solid #1976D2;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: rgba(33, 150, 243, 230);
            }
        """
        
        inactive_style = """
            QPushButton {
                background-color: rgba(240, 240, 240, 150);
                color: #616161;
                border: none;
                border-bottom: 2px solid #E0E0E0;
                font-size: 14px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: rgba(224, 224, 224, 180);
                color: #424242;
            }
        """
        
        if self.current_view == "chat":
            self.chat_tab.setStyleSheet(active_style)
            self.function_tab.setStyleSheet(inactive_style)
        else:
            self.chat_tab.setStyleSheet(inactive_style)
            self.function_tab.setStyleSheet(active_style)
    
    def open_settings(self):
        """打开设置对话框"""
        logger.info("Opening settings dialog")
        self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.show_centered()
        self.settings_dialog.exec_()
    
    def acquire_focus(self):
        # 移除透明窗口设置，使窗口可以接收输入
        hwnd = int(self.winId())
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) & ~win32con.WS_EX_TRANSPARENT)
        # 激活窗口并获取焦点
        self.setWindowState(Qt.WindowMinimized)
        self.setWindowState(Qt.WindowActive)

    def give_back_focus(self):
        # 恢复透明窗口设置
        hwnd = int(self.winId())
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_TRANSPARENT)
        # 将焦点返回给游戏
        HANDLE_OBJ.set_foreground()

    def position_window(self):
        """根据游戏窗口位置调整聊天窗口位置"""
        if HANDLE_OBJ.get_handle():
            try:
                win_bbox = win32gui.GetWindowRect(HANDLE_OBJ.get_handle())
                
                if self.is_expanded:
                    # 展开状态：显示在游戏窗口左下角
                    chat_x = win_bbox[0] + 10
                    chat_y = win_bbox[3] - 610
                else:
                    # 收缩状态：显示在游戏窗口左上角
                    chat_x = win_bbox[0] + 10
                    chat_y = win_bbox[3] - 610
                
                self.move(chat_x, chat_y)
            except Exception as e:
                logger.error(f"Failed to position window: {e}")
                # 默认位置
                self.move(100, 100)
        else:
            # 没有游戏窗口时的默认位置
            self.move(100, 100)

    def on_slash_pressed(self):
        """处理斜杠键按下事件"""
        if win32gui.GetForegroundWindow() != HANDLE_OBJ.get_handle():
            return
        logger.info("Slash pressed - expanding chat")
        self.expand_chat()
    
    def on_esc_pressed(self):
        """处理ESC键按下事件"""
        if win32gui.GetForegroundWindow() != int(self.winId()):
            return
        logger.info("Esc pressed - collapsing chat")
        if self.is_expanded:
            self.collapse_chat()
    
    def update_ui_position(self):
        """定时更新，处理窗口隐藏和位置"""
        active_process_name = get_active_window_process_name()
        if (not active_process_name == PROCESS_NAME) and (not active_process_name == 'python.exe'):
            self.hide()
            if self.settings_dialog:
                self.settings_dialog.reject()
            return
        else:
            if not self.isVisible():
                self.show()
        
        if self.isVisible():
            # 获取游戏窗口位置
            if HANDLE_OBJ.get_handle():
                win_bbox = win32gui.GetWindowRect(HANDLE_OBJ.get_handle())
                if self.last_bbox != win_bbox:
                    self.position_window()
                    self.last_bbox = win_bbox
    
    def update_message(self, message: str):
        if self.current_view == "chat":
            self.chat_view.ui_update_signal.emit("update_ai_message", message)

            
    # def log_poster(self, log_str: str):
    #     """处理格式化日志输出"""
    #     if DEMO_MODE:
    #         if "DEMO" not in log_str:
    #             return
        
    #     # 简化处理，直接添加到聊天
    #     if "\x1b[" in log_str:
    #         import re
    #         clean_text = re.sub(r'\x1b\[[0-9;]*m', '', log_str)
    #     else:
    #         clean_text = log_str
        
    #     if clean_text.strip():
    #         # 通过信号触发UI更新，确保在主线程中执行
    #         self.ui_update_signal.emit("add_log_message", clean_text.strip())