'''朝夕心愿一条龙'''

from whimbox.task.task_template import TaskTemplate, register_step
from whimbox.task import daily_task
from whimbox.task.navigation_task.auto_path_task import AutoPathTask
from whimbox.task.photo_task.daily_photo_task import DailyPhotoTask
from whimbox.config.config import global_config
from whimbox.task.daily_task.cvar import *

class AllInOneTask(TaskTemplate):
    def __init__(self):
        super().__init__("all_in_one_task")
        self.todo_list = None

    @register_step("美鸭梨挖掘")
    def step1(self):
        dig_task = daily_task.DigTask()
        dig_task.task_run()

    @register_step("检查朝夕心愿进度")
    def step2(self):
        zhaoxi_task = daily_task.ZhaoxiTask()
        task_result = zhaoxi_task.task_run()
        self.todo_list = task_result.data
        if self.todo_list is None:
            self.task_stop(msg="朝夕心愿任务已全部完成")
        self.log_to_gui(task_result.message)

    @register_step("开始完成朝夕心愿任务")
    def step3(self):
        task_dict = {
            DAILY_TASK_PICKUP: AutoPathTask("example1_采集测试.json", 5),
            DAILY_TASK_CATCH_INSECT: AutoPathTask("example4_捕虫测试.json", 3),
            DAILY_TASK_GET_BLESS: daily_task.BlessTask(),
            DAILY_TASK_TAKE_PHOTO: DailyPhotoTask(),
        }
        for task_name in self.todo_list:
            if task_name in task_dict:
                task = task_dict[task_name]
                task.task_run()
        
    @register_step("消耗剩余体力")
    def step4(self):
        energy_cost = global_config.get("Game", "energy_cost")
        if energy_cost == "素材激化幻境":
            if DAILY_TASK_JIHUA not in self.todo_list:
                task = daily_task.JihuaTask()
                task.task_run()
            else:
                self.log_to_gui("体力之前已被消耗")
        elif energy_cost == "祝福闪光幻境":
            if DAILY_TASK_GET_BLESS not in self.todo_list:
                task = daily_task.BlessTask()
                task.task_run()
            else:
                self.log_to_gui("体力之前已被消耗")
        else:
            self.log_to_gui("未配置默认消耗体力方式")
    
    @register_step("获取朝夕心愿奖励")
    def step5(self):
        zhaoxi_task = daily_task.ZhaoxiTask()
        task_result = zhaoxi_task.task_run()
        todo_list = task_result.data
        if todo_list is None:
            self.update_task_result(message=task_result.message)
        else:
            self.update_task_result(message=f"仍需手动完成以下任务：{", ".join(todo_list)}")

    @register_step("领取奇迹之旅奖励")
    def step6(self):
        monthly_pass_task = daily_task.MonthlyPassTask()
        monthly_pass_task.task_run()


if __name__ == "__main__":
    task = AllInOneTask()
    result = task.task_run()
    print(result.to_dict())
        