import asyncio
from PyQt5.QtCore import QThread, pyqtSignal
import whimbox.mcp_agent as mcp_agent
from whimbox.common.logger import logger

class QueryWorker(QThread):
    """异步查询工作线程"""
    
    def __init__(self, text, ui_update_signal):
        super().__init__()
        self.text = text
        self.ui_update_signal = ui_update_signal
    
    def run(self):
        """在线程中运行的方法"""
        try:
            # 发送信号移除"正在处理"的消息
            self.ui_update_signal.emit("remove_processing", "")
            
            # 添加空的AI消息容器并显示状态栏
            self.ui_update_signal.emit("add_ai_message", "")
            self.ui_update_signal.emit("status_thinking", "")
            
            # 定义流式回调函数
            def stream_callback(chunk):
                self.ui_update_signal.emit("update_ai_message", chunk)
            
            # 定义状态回调函数
            def status_callback(status_type, message=""):
                self.ui_update_signal.emit(f"status_{status_type}", message)
            
            # 运行异步查询，传入流式回调
            asyncio.run(mcp_agent.query_agent(
                self.text, 
                stream_callback=stream_callback,
                status_callback=status_callback
            ))
            
            # 完成AI消息输出
            self.ui_update_signal.emit("finalize_ai_message", "")
            self.ui_update_signal.emit("status_completed", "")
            
        except Exception as e:
            logger.error(f"AI查询失败: {e}")
            # 发送错误信号
            self.ui_update_signal.emit("handle_error", str(e))
            self.ui_update_signal.emit("status_error", str(e))
        finally:
            self.ui_update_signal.emit("query_finished", "")