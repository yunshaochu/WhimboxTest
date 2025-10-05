from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class CollapsedChatWidget(QWidget):
    """收缩状态的聊天组件"""
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setFixedSize(64, 64)
        self.setAttribute(Qt.WA_StyledBackground, True)  # 允许QWidget设置背景
        self.setStyleSheet("""
            CollapsedChatWidget {
                background-color: rgba(255, 255, 255, 180);
                border-radius: 12px;
                border: 2px solid #E0E0E0;
            }
            CollapsedChatWidget:hover {
                background-color: rgba(255, 255, 255, 220);
                border: 2px solid #2196F3;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 5)
        
        icon_label = QLabel("📦")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; border: none; background: transparent; color: #424242;")
        
        layout.addWidget(icon_label)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)