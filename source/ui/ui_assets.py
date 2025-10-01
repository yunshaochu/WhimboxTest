from source.ui.template.img_manager import LOG_WHEN_TRUE, LOG_ALL, LOG_NONE, LOG_WHEN_FALSE, ImgIcon, GameImg
from source.ui.template.button_manager import Button
from source.ui.template.posi_manager import PosiTemplate, Area
from source.ui.template.text_manager import TextTemplate, Text

# 很多界面左上角都有的文字标题区域
AreaPageTitleFeature = Area()

# 主界面、esc菜单相关
IconPageMainFeature = ImgIcon(print_log=LOG_NONE, threshold=0.99)
IconDungeonFeature = ImgIcon(print_log=LOG_NONE, threshold=0.99)
TextPageEscFeature = Text("美鸭梨", cap_area = AreaPageTitleFeature)
AreaUITime = Area()
AreaEscEntrances = Area()

# loading界面
IconUILoading1 = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
IconUILoading2 = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)

# 大地图相关
IconUIBigmap = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
IconBigMapMaxScale = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonBigMapZoom = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonBigMapTeleport = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
AreaBigMapRegionName = Area()
AreaBigMapRegionSelect = Area()
AreaBigMapTeleporterSelect = Area()
# 大地图材料追踪
AreaBigMapMaterialTypeSelect = Area()
AreaBigMapMaterialSelect = Area()
AreaBigMapMaterialTrackConfirm = Area()

# 大世界采集、跳跃、移动相关的UI
AreaFPickup = Area()
TextFPickUp = Text("拾取", cap_area = AreaFPickup)
AreaFSkip = Area()
TextFSkip = Text("跳过", cap_area = AreaFSkip)
AreaClickSkip = Area()
TextClickSkip = Text("空白区域继续", cap_area = AreaClickSkip)
AreaMovementWalk = Area()
IconMovementWalking = ImgIcon()
AreaMaterialTrackNear = Area()
AreaMaterialGetText = Area()
AreaAbilityButton = Area()

# 钓鱼相关
IconFishingNoFish = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99) # 鱼掉光时候的图标
AreaFishingDetection = Area()  # B区域（鱼进度检测区域）
IconFishingReelIn = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.8)  # 收竿图标
IconFishingStrike = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.8) # 提竿图标
IconFishingPullLine = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.8)  # 拉扯鱼线图标1
IconFishingPullLineAlt = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.8)  # 拉扯鱼线图标2-采星
IconFishingReelLine = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.8)  # 收线图标
IconFishingSkip = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.8) # 跳过

# 每日任务相关
AreaDailyTaskFeature = Area()
TextDailyTaskFeature = Text("每日灵感", cap_area = AreaDailyTaskFeature)
ButtonHuanjingGo = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)

# 幻境挑战页面
TextHuanjingFeature = Text("幻境挑战", cap_area = AreaPageTitleFeature)
AreaHuanjingMonsterEntrace = Area()
TextHuanjingMonsterEntrace = Text("魔物试炼幻境", cap_area = AreaHuanjingMonsterEntrace)
AreaHuanjingBlessEntrace = Area()
TextHuanjingBlessEntrace = Text("祝福闪光幻境", cap_area = AreaHuanjingBlessEntrace)
AreaHuanjingZiyangEntrace = Area()
TextHuanjingZiyangEntrace = Text("奇想滋养幻境", cap_area = AreaHuanjingZiyangEntrace)
AreaHuanjingJihuaEntrace = Area()
TextHuanjingJihuaEntrace = Text("素材激化幻境", cap_area = AreaHuanjingJihuaEntrace)
AreaHuanjingBossEntrace = Area()
TextHuanjingBossEntrace = Text("心之突破幻境", cap_area = AreaHuanjingBossEntrace)

# 祝福闪光幻境相关
TextHuanjingBlessFeature = Text("祝福闪光幻境", cap_area = AreaPageTitleFeature)
AreaBlessHuanjingLevelsSelect = Area()
AreaBlessHuanjingDifficulty3 = Area()
TextBlessHuanjingDifficulty3 = Text("困难", cap_area = AreaBlessHuanjingDifficulty3)
ButtonBlessHuanjingQuickPlay = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonBlessHuanjingNumMax = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonBlessHuanjingConfirm = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)

# 素材激化幻境相关
TextHuanjingJihuaFeature = Text("素材激化幻境", cap_area = AreaPageTitleFeature)
ButtonJihuaInnerGo = Button(print_log=LOG_WHEN_TRUE,threshold=0.99)
AreaTextJihuatai = Area()
TextJihuatai = Text("打开素材激化台", cap_area = AreaTextJihuatai)
AreaJihuaTargetSelect = Area()
AreaJihuaCostSelect = Area()
ButtonJihuaNumMax = Button(print_log=LOG_WHEN_TRUE,threshold=0.99)
ButtonJihuaNumConfirm = Button(print_log=LOG_WHEN_TRUE,threshold=0.99)
ButtonJihuaFinallyConfirm = Button(print_log=LOG_WHEN_TRUE,threshold=0.99)

# 美鸭梨挖掘相关
ButtonDigGather = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonDigGatherConfirm = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonDigAgain = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
AreaDigingNumText = Area()
AreaDigMainTypeSelect = Area()
AreaDigSubTypeSelect = Area()
AreaDigItemSelect = Area()
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

# 换装界面
AreaWardrobeTab1 = Area()
TextWardrobeDressTab = Text("换装", cap_area = AreaWardrobeTab1)
ButtonWardrobeDressDIY = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
# 能力配置界面
AreaWardrobeTab3 = Area()
TextWardrobeAbilityTab = Text("能力配置", cap_area = AreaWardrobeTab3)
AreaWardrobeAbilityBattleText = Area()
TextWardrobeAbilityBattle = Text("净化", cap_area = AreaWardrobeAbilityBattleText)
IconAbilityFloat = ImgIcon()    # 泡泡套跳跃
IconAbilityWing = ImgIcon()    # 飞鸟套跳跃
IconAbilityAnimal = ImgIcon()    # 清洁
IconAbilityInsect = ImgIcon()      # 捕虫
IconAbilityFish = ImgIcon()     # 钓鱼
IconAbilityFly = ImgIcon()      # 滑翔
IconAbilitySmall = ImgIcon()    # 变小
AreaAbilityChange = Area()
ButtonAbilitySave = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)

# 素材相关
IconMaterialTypeAnimal = ImgIcon()
IconMaterialTypePlant = ImgIcon()
IconMaterialTypeInsect = ImgIcon()
IconMaterialTypeFish = ImgIcon()
IconMaterialTypeMonster = ImgIcon()
IconMaterialTypeOther = ImgIcon()
IconMaterialTypeDig1 = ImgIcon()

# 拍照相关
TextPhotoFeature = Text("大喵相机", cap_area = AreaPageTitleFeature)
IconPhotoEdit = ImgIcon(print_log=LOG_WHEN_TRUE, threshold=0.99)
IconPhotoDelete = ImgIcon()
ButtonPhotoDeleteConfirm = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)

# 大月卡，奇迹之旅
TextMonthlyPassFeature = Text("奇迹之旅", cap_area = AreaPageTitleFeature)
ButtonMonthlyPassAward = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonMonthlyPassTab1 = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)
ButtonMonthlyPassTab2 = Button(print_log=LOG_WHEN_TRUE, threshold=0.99)