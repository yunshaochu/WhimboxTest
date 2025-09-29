"""
朝夕心愿
"""

from source.task.task_template import TaskTemplate, register_step
from source.ui.ui import ui_control
from source.ui.page_assets import *
from source.interaction.interaction_core import itt
import time
from source.common.utils.ui_utils import wait_until_appear


zxxy_task_dict = {
    "植物":{
        "score": 200,
        "priority": 5,
        "task_name": "采集"
    },
    "昆虫":{
        "score": 200,
        "priority": 4,
        "task_name": "捕虫"
    },
    "小游戏":{
        "score": 200,
        "priority": 0,
        "task_name": "玩小游戏"
    },
    "活跃能量":{
        "score": 150,
        "priority": 5,
        "task_name": "消耗活跃能量"
    },
    "照片":{
        "score": 100,
        "priority": 5,
        "task_name": "拍照"
    },
    "挖掘":{
        "score": 100,
        "priority": 5,
        "task_name": "美鸭梨挖掘"
    },
    "升级":{
        "score": 100,
        "priority": 5,
        "task_name": "升级祝福闪光"
    },
    "魔气怪":{
        "score": 100,
        "priority": 3,
        "task_name": "打怪"
    },
    "制作":{
        "score": 100,
        "priority": 0,
        "task_name": "制作服装"
    }

}


class ZhaoxiTask(TaskTemplate):
    def __init__(self):
        super().__init__("zhaoxi_task")
        self.current_score = 0


    @register_step("正在前往朝夕心愿")
    def step1(self):
        ui_control.ui_goto(page_zxxy)


    @register_step("查看完成情况")
    def step2(self):
        try:
            time.sleep(2) # 等待分数变化
            score_str = itt.ocr_single_line(AreaZxxyScore, padding=50)
            score = int(score_str.strip())
            if score % 100 != 0:
                raise Exception(f"朝夕心愿分数识别异常:{score_str}")
        except:
            raise Exception(f"朝夕心愿分数识别异常:{score_str}")
        self.current_score = score
        if score == 500:
            return "step4"
        else:
            self.log_to_gui(f"朝夕心愿完成度：{score}/500")
            return "step3"


    @register_step("查看具体任务")
    def step3(self):

        def check_task(task_btn: Button):
            itt.move_and_click(task_btn.click_position())
            time.sleep(0.5)
            if not itt.get_img_existence(IconUIZxxyTaskFinished):
                task_text = itt.ocr_single_line(AreaZxxyTaskText)
                for key, value in zxxy_task_dict.items():
                    if key in task_text:
                        return value
            else:
                return None

        # 获得未完成任务列表
        unfinished_task_list = []
        button_list = [ButtonZxxyTask1, ButtonZxxyTask2, ButtonZxxyTask3, ButtonZxxyTask4, ButtonZxxyTask5]
        for i in range(5):
            unfinished_task = check_task(button_list[i])
            if unfinished_task == None:
                continue
            else:
                self.log_to_gui(f"未完成任务：{unfinished_task['task_name']}")
                unfinished_task_list.append(unfinished_task)
        
        # 根据优先级和分数，判断应该做什么任务
        todo_list = []
        temp_score = self.current_score
        unfinished_task_list.sort(
            key=lambda x: (x['priority'], x['score']),
            reverse=True
        )
        for task in unfinished_task_list:
            if task['priority'] == 0:
                continue
            if temp_score >= 500:
                break
            todo_list.append(task['task_name'])
            temp_score += task['score']
        
        if len(todo_list) > 0:
            self.update_task_result(message=f"需要继续完成以下任务：{", ".join(todo_list)}")
            return "step5"
        else:
            raise Exception("没办法凑齐分数了")
                

    @register_step("领取奖励")
    def step4(self):
        if not itt.get_img_existence(ButtonZxxyRewarded):
            itt.move_and_click(ButtonZxxyRewarded.click_position())
            time.sleep(0.2)
            if wait_until_appear(TextClickSkip):
                itt.key_press('f')
            self.update_task_result(message="成功领取朝夕心愿奖励")
        else:
            self.update_task_result(message="朝夕心愿奖励已被领取过，无需再次领取")


    @register_step("退出朝夕心愿")
    def step5(self):
        ui_control.ui_goto(page_main)
    

if __name__ == "__main__":
    zhaoxi_task = ZhaoxiTask()
    zhaoxi_task.task_run()
    print(zhaoxi_task.task_result)