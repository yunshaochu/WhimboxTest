from whimbox.ui.page import UIPage
from whimbox.ui.ui_assets import *

page_loading = UIPage(check_icon=[IconUILoading1, IconUILoading2])

page_main = UIPage(check_icon=IconPageMainFeature)
page_bigmap = UIPage(check_icon=IconUIBigmap)
page_esc = UIPage(check_icon=TextPageEscFeature)
page_daily_task = UIPage(check_icon=TextDailyTaskFeature)
page_zxxy = UIPage(check_icon=IconUIZxxy)
page_xhsy = UIPage(check_icon=IconUIXhsy)
page_dress = UIPage(check_icon=ButtonWardrobeDressDIY)
page_ability = UIPage(check_icon=TextWardrobeAbilityBattle)
page_huanjing = UIPage(check_icon=TextHuanjingFeature)
page_huanjing_jihua = UIPage(check_icon=TextHuanjingJihuaFeature)
page_huanjing_bless = UIPage(check_icon=TextHuanjingBlessFeature)
page_photo = UIPage(check_icon=TextPhotoFeature)
page_monthly_pass = UIPage(check_icon=TextMonthlyPassFeature)

ui_pages = [
    page_main,
    page_bigmap,
    page_daily_task,
    page_zxxy,
    page_xhsy,
    page_dress,
    page_ability,
    # 以下都是依靠AreaPageTitleFeature文字来判断的页面
    # 放在一起，可以减少ocr次数，提高效率
    page_esc,
    page_huanjing,
    page_huanjing_jihua,
    page_huanjing_bless,
    page_photo,
    page_monthly_pass,
]

page_main.link('m', page_bigmap)
page_main.link('esc', page_esc)
page_main.link('l', page_daily_task)
page_main.link('c', page_dress)
page_main.link('p', page_photo)
page_main.link('j', page_monthly_pass)

page_bigmap.link('m', page_main)

page_esc.link('esc', page_main)

page_daily_task.link('esc', page_main)
page_daily_task.link(ButtonHuanjingGo, page_huanjing)
page_daily_task.link(ButtonZxxyEntrance, page_zxxy)
page_daily_task.link(ButtonXhsyEntrance, page_xhsy)

page_huanjing.link('esc', page_daily_task)
page_huanjing.link(TextHuanjingJihuaEntrace, page_huanjing_jihua)
page_huanjing.link(TextHuanjingBlessEntrace, page_huanjing_bless)

page_huanjing_jihua.link('esc', page_huanjing)
page_huanjing_bless.link('esc', page_huanjing)

page_zxxy.link("esc", page_daily_task)

page_xhsy.link("esc", page_daily_task)

page_dress.link("esc", page_main)
page_dress.link(TextWardrobeAbilityTab, page_ability)

page_ability.link("esc", page_main)

page_photo.link("esc", page_main)

page_monthly_pass.link("esc", page_main)