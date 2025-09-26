from source.task.task_template import TaskTemplate, register_step
from source.interaction.interaction_core import itt
from source.common.cvars import DEBUG_MODE
from source.ability.ability import ability_manager
from source.ability.cvar import *

class CatchBugTask(TaskTemplate):
    def __init__(self, bug_name: str):
        super().__init__("catch_bug_task")
        self.bug_name = bug_name

    @register_step("切换捕虫能力")
    def step1(self):
       ability_manager.change_ability(ABILITY_NAME_INSECT)

    @ register_step("开启地图追踪")
    def step2(self):
        pass