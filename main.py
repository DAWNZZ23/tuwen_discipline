import flet as ft

# 🌟 终极魔法：四大天王齐聚主干！
from view_stats import load_stats_ui
from view_calendar import create_calendar_view
from view_checkin import create_checkin_view


def main(page: ft.Page):
    # 1. 窗口基础设置
    page.title = "吐温自省"
    page.window_width = 400
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = ft.padding.only(top=45, left=15, right=15, bottom=10)

    # ================= [模块载入与拼装] =================

    # 模块 A：载入日历 (拿到 UI 容器和专门的刷新函数)
    calendar_container, update_calendar_fn = create_calendar_view(page)

    # 模块 B：载入打卡 (顺便把日历的刷新函数传给它，让它打卡完自动更新日历)
    checkin_container = create_checkin_view(page, on_submit_success=update_calendar_fn)

    # 模块 C：统计容器 (初始为空，点击时再加载)
    stats_container = ft.Column(
        controls=[], scroll="adaptive", expand=True, visible=False
    )

    # ================= [导航与页面切换逻辑] =================
    def switch_tab(e, index):
        # 先把所有页面隐藏
        checkin_container.visible = False
        stats_container.visible = False
        calendar_container.visible = False

        # 再根据点击的按钮显示对应页面
        if index == 0:
            checkin_container.visible = True
        elif index == 1:
            stats_container.controls = load_stats_ui()  # 实时加载统计数据
            stats_container.visible = True
        elif index == 2:
            update_calendar_fn()  # 实时刷新日历数据
            calendar_container.visible = True
        page.update()

    main_content = ft.Column(
        controls=[checkin_container, stats_container, calendar_container],
        expand=True
    )

    bottom_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.FilledTonalButton(content=ft.Text("📝打卡", size=14), on_click=lambda e: switch_tab(e, 0),
                                     expand=True, height=45),
                ft.FilledTonalButton(content=ft.Text("📊统计", size=14), on_click=lambda e: switch_tab(e, 1),
                                     expand=True, height=45),
                ft.FilledTonalButton(content=ft.Text("📅日历", size=14), on_click=lambda e: switch_tab(e, 2),
                                     expand=True, height=45),
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            spacing=5
        ),
        padding=5,
        bgcolor="#f3f4f6",
        border_radius=10
    )

    # 把主要内容和底部导航栏加到页面上
    page.add(main_content, bottom_bar)

    # 软件启动时静默刷新一次日历
    update_calendar_fn()


ft.run(main)
