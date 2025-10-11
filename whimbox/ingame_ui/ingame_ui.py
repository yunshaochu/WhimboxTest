"""
游戏内UI模块 - 重构版本

这个模块提供了一个简洁的入口点，将原来的大文件拆分为多个组件：
- components/: UI组件（ChatMessage, ChatMessageWidget, CollapsedChatWidget, AIStatusBar）
- workers/: 工作线程（QueryWorker）
- main_ui.py: 主UI类（IngameUI）
"""

import sys
from PyQt5.QtWidgets import QApplication
from whimbox.ingame_ui.main_ui import IngameUI

# 全局应用和UI实例
ingame_ui_app = QApplication(sys.argv)
win_ingame_ui = IngameUI()

# 全局样式表
_style = """
QWidget {
    font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
    border: none;
    background: none;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
"""

ingame_ui_app.setStyleSheet(_style)

def run_ingame_ui():
    """运行游戏内UI"""
    win_ingame_ui.show()
    ingame_ui_app.exec_()

if __name__ == '__main__':
    print('AI游戏助手聊天UI已启动')
    print('按下 "/" 键展开聊天界面')
    print('按下 ESC 键收缩聊天界面')
    
    run_ingame_ui()