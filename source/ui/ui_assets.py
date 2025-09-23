from source.ui.template.img_manager import LOG_WHEN_TRUE, LOG_ALL, LOG_NONE, LOG_WHEN_FALSE, ImgIcon, GameImg
from source.ui.template.button_manager import Button
from source.ui.template.posi_manager import PosiTemplate, Area
from source.ui.template.text_manager import TextTemplate, Text

# 主界面、esc菜单相关
IconUIMeiyali = ImgIcon(print_log=LOG_NONE, threshold=0.99)
IconUICollection = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
AreaUITime = Area()

# loading界面
IconUILoading = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)

# 大地图相关
IconUIBigmap = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
IconBigMapMaxScale = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonBigMapZoom = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
IconBigMapCheckPointSelect = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonBigMapTeleport = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
AreaBigMapRegionName = Area()
AreaBigMapRegionSelect = Area()

# 大世界采集、跳跃、移动相关的UI
AreaFPickup = Area()
TextFPickUp = Text("拾取", cap_area = AreaFPickup)
AreaFSkip = Area()
TextFSkip = Text("跳过", cap_area = AreaFSkip)
AreaClickSkip = Area()
TextClickSkip = Text("空白区域继续", cap_area = AreaClickSkip)
AreaMovementWalk = Area()
IconMovementWalking = ImgIcon()

# 每日任务相关
IconUIDailyTask = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonHuanjingGo = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
IconUIHuanjing = ImgIcon(is_bbg=True, bbg_posi=[120, 37, 246, 68], print_log=LOG_WHEN_TRUE, threshold=0.99)

# 素材激化相关
ButtonJihuaGo = Button(print_log=LOG_WHEN_TRUE,threshold=0.90)
IconUIJihuaInner = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonJihuaInnerGo = Button(print_log=LOG_WHEN_TRUE,threshold=0.99)
AreaTextJihuatai = Area()
TextJihuatai = Text("打开素材激化台", cap_area = AreaTextJihuatai)
ButtonJihuaPaopao = Button(print_log=LOG_WHEN_TRUE,threshold=0.99)
ButtonJihuaPuling = Button(print_log=LOG_WHEN_TRUE,threshold=0.99)
ButtonJihuaSixian = Button(print_log=LOG_WHEN_TRUE,threshold=0.99)
IconUIJihuaSelect = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
AreaUIJihuaSelect = Area()
ButtonJihuaNumMax = Button(print_log=LOG_WHEN_TRUE,threshold=0.99)
ButtonJihuaNumConfirm = Button(print_log=LOG_WHEN_TRUE,threshold=0.99)
ButtonJihuaFinallyConfirm = Button(print_log=LOG_WHEN_TRUE,threshold=0.99)

# 美鸭梨挖掘相关
ButtonDigGo = Button(print_log=LOG_WHEN_TRUE, threshold=0.9)
IconUIDig = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonDigGather = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonDigGatherConfirm = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
AreaTextDigingNum = Area()
ButtonDigType1 = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonDigType1Fish = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonDigType1Insect = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonDigType1Plant = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonDigType1Animal = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonDigType2 = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
AreaUIDigItemSelect = Area()
ButtonDigConfirm = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonDigTime20h = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)

# 朝夕心愿相关
ButtonZxxyEntrance = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
IconUIZxxy = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
AreaZxxyScore = Area()
ButtonZxxyRewarded = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonZxxyTask1 = Button()
ButtonZxxyTask2 = Button()
ButtonZxxyTask3 = Button()
ButtonZxxyTask4 = Button()
ButtonZxxyTask5 = Button()
AreaZxxyTaskText = Area()
IconUIZxxyTaskFinished = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)

# 星海拾遗相关
ButtonXhsyEntrance = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
IconUIXhsy = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)

# 游戏自己的美术素材
T_Icon_item_AN0068R2 = GameImg() # 玉簪蚂蚱
T_Icon_item_AN0080 = GameImg() # 插梳鱼
T_UI_icon_004 = GameImg() # 纯真丝线
T_UI_icon_006 = GameImg() # 闪光粒子