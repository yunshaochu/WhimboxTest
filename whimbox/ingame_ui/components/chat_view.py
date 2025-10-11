from typing import List
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from whimbox.common.logger import logger
from .chat_message import ChatMessage, ChatMessageWidget


class ChatView(QWidget):
    """聊天视图组件"""
    message_sent = pyqtSignal(str)  # 发送消息信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 消息管理
        self.chat_messages: List[ChatMessage] = []
        self.max_messages = 100
        
        # UI组件
        self.chat_scroll_area = None
        self.chat_container = None
        self.chat_layout = None
        self.input_line_edit = None
        self.send_button = None
        
        # 初始化UI
        self.init_ui()
    
    def init_ui(self):
        """初始化聊天视图UI"""
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
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
        
        return message
    
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
    
    def send_message(self):
        """发送消息"""
        text = self.input_line_edit.text().strip()
        if not text:
            return
        
        # 清空输入框
        self.input_line_edit.clear()
        
        # 发出消息信号
        self.message_sent.emit(text)
    
    def set_focus_to_input(self):
        """设置焦点到输入框"""
        if self.input_line_edit:
            self.input_line_edit.setFocus()
    
    def get_messages(self) -> List[ChatMessage]:
        """获取所有消息"""
        return self.chat_messages
    
    def has_messages(self) -> bool:
        """检查是否有消息"""
        return len(self.chat_messages) > 0

