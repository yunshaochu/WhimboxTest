from typing import List
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

from whimbox.ingame_ui.components import ChatMessage, ChatMessageWidget, CollapsedChatWidget, SettingsDialog
from whimbox.ingame_ui.workers import QueryWorker

update_time = 500  # ui更新间隔，ms

class IngameUI(QWidget):
    ui_update_signal = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        
        # 状态管理
        self.is_expanded = False
        self.chat_messages: List[ChatMessage] = []
        self.max_messages = 100  # 最大消息数量
        
        # UI组件
        self.collapsed_widget = None
        self.expanded_widget = None
        self.chat_scroll_area = None
        self.chat_container = None
        self.input_line_edit = None
        self.send_button = None
        self.chat_layout = None
        self.settings_dialog = None
        
        # 初始化UI
        self.init_ui()
        
        # 计时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui_position)
        self.timer.start(update_time)
        
        # 工作线程管理
        self.current_worker = None
        
        # 连接UI更新信号到槽函数（这个连接是在主线程中的）
        self.ui_update_signal.connect(self.handle_ui_update)

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
    
    def handle_ui_update(self, operation: str, param: str = ""):
        """处理UI更新操作（总是在主线程中执行）"""
        if operation == "remove_processing":
            if self.chat_messages and self.chat_messages[-1].content == "正在处理您的请求...":
                self.chat_messages.pop()
                self.refresh_chat_display()
        elif operation == "handle_error":
            # 移除"正在处理"的消息
            if self.chat_messages and self.chat_messages[-1].content == "正在处理您的请求...":
                self.chat_messages.pop()
                self.refresh_chat_display()
            self.add_message(f"抱歉，处理您的请求时出现错误: {param}", 'error')
        elif operation == "query_finished":
            if self.current_worker:
                self.current_worker.deleteLater()
                self.current_worker = None
        elif operation == "add_ai_message":
            # 添加一个正在处理的AI消息作为流式输出的容器
            message = ChatMessage("", 'ai')
            message.is_processing = True
            self.chat_messages.append(message)
            self.refresh_chat_display()
        elif operation == "update_ai_message":
            # 更新最后一条AI消息的内容
            if self.chat_messages and self.chat_messages[-1].message_type == 'ai':
                self.chat_messages[-1].content += param
                # 更新对应的widget
                self.update_last_ai_message_widget()
        elif operation == "finalize_ai_message":
            # 完成AI消息输出
            if self.chat_messages and self.chat_messages[-1].message_type == 'ai':
                self.chat_messages[-1].is_processing = False
                # 确保消息内容不为空
                if not self.chat_messages[-1].content.strip():
                    self.chat_messages[-1].content = "AI返回空内容"
                self.update_last_ai_message_widget()
        elif operation.startswith("status_"):
            # 处理状态更新
            status_type = operation[7:]  # 去掉"status_"前缀
            if status_type == "on_tool_start":
                self.give_back_focus()
            if status_type == "on_tool_end":
                self.acquire_focus()
            self.update_last_ai_status(status_type, param)
    
    def update_last_ai_message_widget(self):
        """更新最后一个AI消息的widget"""
        if not self.chat_layout:
            return
        
        # 找到最后一个AI消息的widget
        for i in range(self.chat_layout.count() - 1, -1, -1):
            item = self.chat_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ChatMessageWidget):
                widget = item.widget()
                if widget.message.message_type == 'ai':
                    widget.update_content(widget.message.content)
                    self.scroll_to_bottom()
                    break
    
    def update_last_ai_status(self, status_type: str, message: str = ""):
        """更新最后一个AI消息的状态"""
        if not self.chat_layout:
            return
        
        # 找到最后一个AI消息的widget
        for i in range(self.chat_layout.count() - 1, -1, -1):
            item = self.chat_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), ChatMessageWidget):
                widget = item.widget()
                if widget.message.message_type == 'ai':
                    widget.update_status(status_type, message)
                    self.scroll_to_bottom()
                    break
    
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
        
        # 聊天显示区域
        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.chat_scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                background-color: rgba(240, 240, 240, 150);
            }
            QScrollBar:vertical {
                background-color: #F5F5F5;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #BDBDBD;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #9E9E9E;
            }
        """)
        
        self.chat_container = QWidget()
        self.chat_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(4, 4, 4, 4)
        self.chat_layout.setSpacing(4)
        self.chat_layout.addStretch()  # 添加stretch使消息从底部开始
        
        self.chat_scroll_area.setWidget(self.chat_container)
        
        # 输入区域
        input_layout = QHBoxLayout()
        self.input_line_edit = QLineEdit()
        self.input_line_edit.setPlaceholderText("请输入命令...")
        self.input_line_edit.returnPressed.connect(self.send_message)
        self.input_line_edit.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #424242;
                border: 1px solid #E0E0E0;
                border-radius: 16px;
                padding: 8px 16px;
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
                background-color: #FAFAFA;
            }
            QLineEdit::placeholder {
                color: #9E9E9E;
            }
        """)
        
        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 16px;
                padding: 8px 16px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        
        input_layout.addWidget(self.input_line_edit)
        input_layout.addWidget(self.send_button)
        
        # 组装布局
        layout.addLayout(title_layout)
        layout.addWidget(self.chat_scroll_area, 1)
        layout.addLayout(input_layout)
    
    def add_message(self, content: str, message_type: str):
        """添加消息到聊天列表"""
        # 限制消息数量
        if len(self.chat_messages) >= self.max_messages:
            self.chat_messages = self.chat_messages[-self.max_messages//2:]
        
        message = ChatMessage(content, message_type)
        self.chat_messages.append(message)
        
        # 只添加新消息到UI
        self.add_message_to_ui(message)
    
    def add_message_to_ui(self, message: ChatMessage):
        """将消息添加到UI中"""
        if self.chat_layout is None:
            return
        
        # 移除stretch（如果存在）
        stretch_item = self.chat_layout.itemAt(self.chat_layout.count() - 1)
        if stretch_item and stretch_item.spacerItem():
            self.chat_layout.removeItem(stretch_item)
        
        # 添加消息组件
        message_widget = ChatMessageWidget(message)
        self.chat_layout.addWidget(message_widget)
        
        # 重新添加stretch
        self.chat_layout.addStretch()
        
        # 滚动到底部
        QTimer.singleShot(50, self.scroll_to_bottom)
    
    def refresh_chat_display(self):
        """刷新整个聊天显示"""
        if self.chat_layout is None:
            return
        
        # 清空现有组件
        while self.chat_layout.count():
            child = self.chat_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # 重新添加所有消息
        for message in self.chat_messages:
            message_widget = ChatMessageWidget(message)
            self.chat_layout.addWidget(message_widget)
        
        # 添加stretch
        self.chat_layout.addStretch()
        
        # 滚动到底部
        QTimer.singleShot(50, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        """滚动到聊天区域底部"""
        if self.chat_scroll_area:
            scrollbar = self.chat_scroll_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
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
        QTimer.singleShot(100, lambda: self.input_line_edit.setFocus() if self.input_line_edit else None)
        
        # 添加欢迎消息（仅在首次展开时）
        if not self.chat_messages:
            self.add_message("👋 您好！我是奇想盒📦，请告诉我你想做什么？。", 'ai')
    
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
    
    def send_message(self):
        """发送消息"""
        text = self.input_line_edit.text().strip()
        if not text:
            return
        
        # 如果已有工作线程在运行，则忽略
        if self.current_worker and self.current_worker.isRunning():
            return

        # 添加用户消息
        self.add_message(text, 'user')
        self.input_line_edit.clear()
        
        self.add_message("正在处理您的请求...", 'ai')
        
        # 创建并启动工作线程
        self.current_worker = QueryWorker(text, self.ui_update_signal)
        
        # 启动线程
        self.current_worker.start()
    
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