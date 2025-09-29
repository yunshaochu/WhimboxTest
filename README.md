![logo](/doc/logo.png)
~~不会画画，先放个红温星凑合一下~~
# Whimbox(奇想盒)
Whimbox，一个基于大语言模型和图像识别技术的游戏AI智能体，带给你全新的游戏体验！

## 运行
⚠️目前项目仍在开发阶段，只建议有python开发能力的用户使用。
1. 安装依赖（需要python3.12）
* 开发者建议手动安装依赖
```shell
pip install -r requirements.txt
# 安装paddleocr运行环境（可选，目前默认使用rapidocr，也可以不装）
python -m pip install paddlepaddle-gpu==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
```
* 其他用户可运行自动安装脚本`setup_env.bat`


2. 创建配置文件
```
将config目录下的config_example.ini重命名为config.ini
修改Agent下的配置项修改为自己的大模型api（只要是openai格式的都可以）
```
3. 创建提示词
```
将config目录下的prompt_example.txt重命名为prompt.txt
按自己喜好添加提示词，也可以不修改
```
4. 打开游戏，将游戏设置为窗口模式，分辨率1920*1080
* 开发者请用管理员权限运行ide，并运行`whimbox.py`
* 其他用户可用管理员权限运行一键启动脚本`run.bat`

5. 程序启动后请稍等片刻。在游戏界面的左侧看到📦图标后，按`/`打开对话框，按`esc`关闭对话框

## 已有功能
* 每日任务
    * 自动美鸭梨挖掘
    * 自动素材激化幻境
    * 自动检查朝夕心愿
* 自动跑图
    * 跑图路线录制、编辑
    * 自动跑图（暂时只支持大世界和星海）
    * 自动采集、捕虫、清洁、钓鱼
* AI对话
    * 通过自然语言编排以上所有功能
    * 随时中断任务

## 未来计划
1. 框架完善：回退机制、重试机制。
2. 多地图适配
3. 自动战斗
4. 自动弹琴（我必须立刻演奏春日影！）
5. 家园适配
6. 单独的启动器

## 注意事项
* Whimbox不会修改游戏文件、读写游戏内存，只会截图和模拟鼠标键盘，理论上不会被封号。但游戏的用户条款非常完善，涵盖了所有可能出现的情况。所以使用Whimbox导致的一切后果请自行承担。
* 由于游戏本身已经消耗PC的大量性能，图像识别还会额外消耗性能，所以目前仅支持中高配PC运行，正式发布后会推出云游戏版本。
* Whimbox目前仅支持1920x1080窗口化运行的游戏。

## 致谢
感谢各个大世界游戏开源项目的先行者，供Whimbox学习参考。
* [原神小助手·GIA](https://github.com/infstellar/genshin_impact_assistant)
* [更好的原神·BetterGI](https://github.com/babalae/better-genshin-impact)

感谢chatgpt、cursor、claude等各种AI模型和AI编程工具

## 加入开发
目前项目仅完成了基本框架的验证，还有大量功能需要开发和适配。如果你对此感兴趣，欢迎加入一起研究。开发Q群：821908945。

### 项目结构
```
Whinbox/
├── assets/                          
│   ├── imgs/                     # 图像资源
│   │   ├── Game/                 # 游戏解包素材
│   │   ├── Maps/                 # 地图相关资源
│   │   ├── Windows/              # 游戏UI截图
│   ├── paths/                    # 自动跑图脚本
│   └── PPOCRModels/              # OCR模型文件
├── source/                        
│   ├── ability/                  # 能力切换模块
│   ├── action/                   # 动作模块（拾取、钓鱼、战斗等等）
│   ├── api/                      # ocr，yolo等第三方模型
│   ├── common/                   # 公共模块（日志、工具等等）
│   ├── config/                   # 配置模块
│   ├── dev_tool/                 # 开发工具
│   ├── ingame_ui/                # 游戏内聊天框
│   ├── interaction/              # 交互核心模块（截图、操作）
│   ├── map/                      # 地图模块（小地图识别，大地图操作）
│   ├── task/                     # 任务模块（各种功能脚本，供mcp调用）
│   │   ├── daily_task/           # 各种日常任务的脚本
│   │   └── navigation_task/      # 自动寻路脚本
│   ├── ui/                       # 游戏UI模块（页面、UI）
│   ├── view_and_move/            # 视角和移动模块
│   ├── mcp_agent.py              # 大模型agent
│   └── mcp_server.py             # MCP服务器
├── config/                       # 配置文件
│   ├── config.ini                # 程序的配置文件
│   └── prompt.txt                # 大模型提示词
├── Logs/                         # 日志文件
├── whimbox.py                    # 主程序入口
```
### MCP工具编写
可参考`source\task\daily_task`内的几个task，并在`source\mcp_server.py`中注册，就能被大模型调用。

### 自动跑图路线录制
详情请查看 [如何录制和编辑跑图路线](./assets/paths/readme.md)
