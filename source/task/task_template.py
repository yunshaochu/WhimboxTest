# 因为我们的task将直接被mcp调用
# 所以就不整原项目thread管理那一套了，怎么简单怎么来
from source.common.logger import logger
from source.ingame_ui.ingame_ui import win_ingame_ui
import time
from source.common.cvars import DEBUG_MODE

STATE_TYPE_SUCCESS = "success"
STATE_TYPE_ERROR = "error"

class state:
    def __init__(self, type="", msg=""):
        self.type = type
        self.msg = msg

class TaskStep:
    def __init__(self, func, name=None, state_type="", state_msg=""):
        self.func = func
        self.state = state(state_type, state_msg)
        self.name = name or func.__name__

    def run(self):
        """运行步骤函数，返回下一步的名称（可选）"""
        return self.func()

def register_step(state_msg=""):
    """类方法装饰器，用于标记需要注册的步骤"""
    def wrapper(func):
        func._register_step = True
        func._state_msg = state_msg
        return func
    return wrapper

class TaskResult:
    def __init__(self, status="success", message=""):
        self.status = status
        self.message = message
    
    def to_dict(self):
        return self.__dict__

    def __str__(self) -> str:
        return f"{{'status': {self.status}, 'message': {self.message}}}"

class TaskTemplate:
    def __init__(self, name=""):
        self.name = name
        self.task_stop_flag = False
        self.step_sleep = 0.2   # 步骤执行后等待时间
        self.steps_dict = {}    # {step_name: TaskStep} 步骤字典
        self.step_order = []    # [step_name, ...] 默认执行顺序
        self.current_step: TaskStep = None
        self.error_step = TaskStep(lambda step, task: None, STATE_TYPE_ERROR, "")
        self.task_result = TaskResult()
        self.__auto_register_steps()

    def __auto_register_steps(self):
        """自动注册带有_register_step标记的方法"""
        # 获取类的所有方法，包括继承的
        for method_name in dir(self):
            # 跳过私有方法和特殊方法
            if method_name.startswith('__'):
                continue
            
            method = getattr(self, method_name)
            # 检查是否是可调用的方法且有注册标记
            if callable(method) and hasattr(method, "_register_step"):
                task_step = TaskStep(method, method_name, STATE_TYPE_SUCCESS, method._state_msg)
                self.steps_dict[method_name] = task_step
                self.step_order.append(method_name)

    def on_error(self, state_msg=""):
        """定义 error_step"""
        def wrapper(func):
            self.error_step = TaskStep(func, "error_step", STATE_TYPE_ERROR, state_msg)
            return func
        return wrapper

    def task_run(self):
        """核心执行逻辑"""
        current_step_name = self.step_order[0] if self.step_order else None
        
        try:
            while current_step_name and not self.task_stop_flag:
                # 获取当前步骤
                step = self.steps_dict.get(current_step_name)
                if not step:
                    raise Exception(f"步骤 '{current_step_name}' 不存在")
                
                self.current_step = step
                
                # 显示步骤信息
                self.log_to_gui(step.state.msg)
                
                # 运行步骤
                next_step_name = step.run()
                
                # 确定下一步
                if next_step_name:
                    # 步骤函数指定了下一步
                    current_step_name = next_step_name
                else:
                    # 使用默认顺序的下一步
                    current_index = self.step_order.index(current_step_name)
                    if current_index + 1 < len(self.step_order):
                        current_step_name = self.step_order[current_index + 1]
                    else:
                        # 已到达最后一步
                        current_step_name = None
                
                time.sleep(self.step_sleep)

        except Exception as e:
            self.handle_exception(e)
            self.error_step.state.msg = str(e)
            self.current_step = self.error_step
            self.log_to_gui(self.error_step.state.msg, is_error=True)
            self.task_result = TaskResult('error', self.error_step.state.msg)
            if DEBUG_MODE:
                import traceback
                logger.error(traceback.format_exc())

        finally:
            return self.task_result


    def handle_exception(self, e):
        '''处理异常，如果子类有异常要处理，就实现这个方法'''
        pass

    def task_stop(self):
        self.task_stop_flag = True

    def get_state_msg(self):
        """获得当前任务的状态信息，供agent显示"""
        return self.current_step.state.msg if self.current_step else ""

    def log_to_gui(self, msg, is_error=False):
        if not is_error:
            msg = f"✅ {msg}\n"
        else:
            msg = f"❌ {msg}\n"
        if win_ingame_ui:
            win_ingame_ui.ui_update_signal.emit("update_ai_message", msg)
        logger.info(msg)

    def update_task_result(self, status="success", message=""):
        self.task_result = TaskResult(status, message)