from typing import Dict, Any
import win32gui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import asyncio

from whimbox.common.handle_lib import HANDLE_OBJ
from whimbox.common.logger import logger
from whimbox.config.default_config import DEFAULT_CONFIG
from whimbox.config.config import global_config
from whimbox.mcp_agent import mcp_agent


class SaveConfigWorker(QThread):
    """异步保存配置的Worker"""
    finished = pyqtSignal(bool, str)  # 成功/失败, 错误信息
    
    def __init__(self, config_data: Dict[str, Any]):
        super().__init__()
        self.config_data = config_data
    
    def run(self):
        """在后台线程中执行保存操作"""
        try:
            agent_modified = False
            # 更新配置值
            for widget_key, value in self.config_data.items():
                section, key = widget_key.split('.')
                # 如果修改了Agent的配置，需要重启mcp_agent
                if section == "Agent":
                    org_value = global_config.get(section, key)
                    if org_value != value:
                        agent_modified = True
                global_config.set(section, key, value)
            
            # 如果修改了Agent配置，重启mcp_agent
            if agent_modified:
                logger.info("agent配置修改，重启mcp_agent")
                asyncio.run(mcp_agent.start())
            
            # 保存配置到文件
            if global_config.save():
                logger.info("配置保存成功")
                self.finished.emit(True, "")
            else:
                logger.error("保存配置失败")
                self.finished.emit(False, "保存配置失败！")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            self.finished.emit(False, f"保存配置失败: {e}")


class SettingsDialog(QDialog):
    """设置对话框，用于修改配置文件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.input_widgets = {}  # 存储输入控件的引用
        self.save_button = None  # 保存按钮引用
        self.cancel_button = None  # 取消按钮引用
        self.save_worker = None  # 保存配置的Worker
        
        self.init_ui()
        self.load_config()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("⚙️ 设置")
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(600, 500)
        
        # 创建主容器（用于圆角背景）
        main_container = QWidget(self)
        main_container.setObjectName("mainContainer")
        main_container.setStyleSheet("""
            #mainContainer {
                background-color: #F5F5F5;
                border-radius: 12px;
            }
        """)
        
        # 主布局
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("⚙️ 设置")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2196F3;
                padding: 5px 0;
            }
        """)
        main_layout.addWidget(title_label)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
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
        
        # 配置容器
        config_container = QWidget()
        config_layout = QVBoxLayout(config_container)
        # config_layout.setContentsMargins(15, 15, 15, 15)
        # config_layout.setSpacing(10)
        
        # 为每个配置节创建分组
        for section_name, section_data in DEFAULT_CONFIG.items():
            if section_name == "General":
                continue
            group_box = self.create_section_group(section_name, section_data)
            config_layout.addWidget(group_box)
        
        config_layout.addStretch()
        scroll_area.setWidget(config_container)
        main_layout.addWidget(scroll_area)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.save_button = QPushButton("保存")
        self.save_button.setFixedHeight(40)
        self.save_button.clicked.connect(self.save_config)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #A5D6A7;
                color: #E0E0E0;
            }
        """)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c2170a;
            }
            QPushButton:disabled {
                background-color: #FFCDD2;
                color: #E0E0E0;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # 设置主容器大小和位置
        main_container.setFixedSize(600, 500)
        
        # 创建对话框布局
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(main_container)
    
    def create_section_group(self, section_name: str, section_data: Dict[str, Any]) -> QGroupBox:
        """为每个配置节创建分组框"""
        if section_name == "General":
            cn_name = "通用"
        elif section_name == "Agent":
            cn_name = "大模型"
        elif section_name == "Game":
            cn_name = "游戏"
        else:
            cn_name = section_name
        group_box = QGroupBox(cn_name)
        group_box.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #424242;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #2196F3;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        for key, config_item in section_data.items():
            item_widget = self.create_config_item(section_name, key, config_item)
            layout.addWidget(item_widget)
        
        group_box.setLayout(layout)
        return group_box
    
    def create_config_item(self, section: str, key: str, config_item: Dict[str, Any]) -> QWidget:
        """创建单个配置项的控件"""
        item_widget = QWidget()
        item_layout = QVBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 5, 5, 5)
        item_layout.setSpacing(5)
        
        # 标签和描述
        label_text = config_item['description']
        
        label = QLabel(label_text)
        label.setWordWrap(True)
        label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 16px;
            }
        """)
        item_layout.addWidget(label)
        
        # 根据值类型创建不同的输入控件
        value = config_item.get('value', '')
        
        # 判断是否是布尔值
        if isinstance(value, bool) or (isinstance(value, str) and value.lower() in ['true', 'false']):
            input_widget = QCheckBox()
            is_checked = value if isinstance(value, bool) else value.lower() == 'true'
            input_widget.setChecked(is_checked)
            input_widget.setStyleSheet("""
                QCheckBox {
                    font-size: 16px;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                }
            """)
        # 判断是否是数字
        elif isinstance(value, (int, float)) or (isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit()):
            input_widget = QLineEdit(str(value))
            input_widget.setPlaceholderText("请输入数字")
            # 设置验证器
            if isinstance(value, int) or (isinstance(value, str) and '.' not in value):
                input_widget.setValidator(QIntValidator())
            else:
                input_widget.setValidator(QDoubleValidator())
            input_widget.setStyleSheet("""
                QLineEdit {
                    padding: 5px;
                    border: 1px solid #BDBDBD;
                    border-radius: 4px;
                    font-size: 16px;
                    background-color: white;
                }
                QLineEdit:focus {
                    border: 2px solid #2196F3;
                }
            """)
        else:
            # 默认使用文本输入
            input_widget = QLineEdit(str(value))
            input_widget.setPlaceholderText("请输入值")
            input_widget.setStyleSheet("""
                QLineEdit {
                    padding: 5px;
                    border: 1px solid #BDBDBD;
                    border-radius: 4px;
                    font-size: 16px;
                    background-color: white;
                }
                QLineEdit:focus {
                    border: 2px solid #2196F3;
                }
            """)
        
        item_layout.addWidget(input_widget)
        
        # 保存控件引用
        self.input_widgets[f"{section}.{key}"] = input_widget
        
        return item_widget
    
    def load_config(self):
        """从 global_config 加载配置到界面"""
        try:
            # 更新输入控件的值
            for widget_key, widget in self.input_widgets.items():
                section, key = widget_key.split('.')
                
                # 从 global_config 获取值
                value = global_config.get(section, key)
                
                if isinstance(widget, QCheckBox):
                    # 对于布尔值，使用 get_bool 方法
                    is_checked = global_config.get_bool(section, key)
                    widget.setChecked(is_checked)
                elif isinstance(widget, QLineEdit):
                    # 对于数字，尝试使用对应的类型方法
                    if widget.validator():
                        if isinstance(widget.validator(), QIntValidator):
                            value = str(global_config.get_int(section, key))
                        elif isinstance(widget.validator(), QDoubleValidator):
                            value = str(global_config.get_float(section, key))
                    widget.setText(str(value))
                        
            logger.info("配置加载成功")
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            QMessageBox.warning(self, "错误", f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置到 global_config"""
        try:
            # 检查是否已经有worker在运行
            if self.save_worker and self.save_worker.isRunning():
                return
            
            # 收集配置数据
            config_data = {}
            for widget_key, widget in self.input_widgets.items():
                # 获取控件的值
                if isinstance(widget, QCheckBox):
                    value = 'true' if widget.isChecked() else 'false'
                elif isinstance(widget, QLineEdit):
                    value = widget.text()
                else:
                    value = ''
                config_data[widget_key] = value
                
            
            # 禁用按钮并显示加载状态
            self.save_button.setEnabled(False)
            self.cancel_button.setEnabled(False)
            self.save_button.setText("⏳ 保存中...")
            
            # 创建Worker并启动
            self.save_worker = SaveConfigWorker(config_data)
            self.save_worker.finished.connect(self.on_save_finished)
            self.save_worker.start()
            
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            QMessageBox.critical(self, "错误", f"保存配置失败: {e}")
            self.restore_buttons()
    
    def on_save_finished(self, success: bool, error_msg: str):
        """保存完成的回调"""
        self.restore_buttons()
        
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "错误", error_msg)
    
    def restore_buttons(self):
        """恢复按钮状态"""
        self.save_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        self.save_button.setText("保存")
    
    def show_centered(self):
        """在游戏窗口中央显示对话框"""
        if HANDLE_OBJ.get_handle():
            try:
                # 获取游戏窗口的位置和大小
                game_rect = win32gui.GetWindowRect(HANDLE_OBJ.get_handle())
                game_x, game_y, game_right, game_bottom = game_rect
                game_width = game_right - game_x
                game_height = game_bottom - game_y
                
                # 计算对话框居中位置
                dialog_x = game_x + (game_width - self.width()) // 2
                dialog_y = game_y + (game_height - self.height()) // 2
                
                self.move(dialog_x, dialog_y)
            except Exception as e:
                logger.error(f"Failed to center dialog: {e}")
                # 如果失败，使用屏幕居中
                screen = QApplication.desktop().screenGeometry()
                self.move((screen.width() - self.width()) // 2,
                         (screen.height() - self.height()) // 2)
        else:
            # 没有游戏窗口时使用屏幕居中
            screen = QApplication.desktop().screenGeometry()
            self.move((screen.width() - self.width()) // 2,
                     (screen.height() - self.height()) // 2)
        
        self.show()
        self.raise_()
        self.activateWindow()

