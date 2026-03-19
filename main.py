import flet as ft

# 🌟 导入你的四大金刚模块！
from view_stats import load_stats_ui
from view_calendar import create_calendar_view
from view_checkin import create_checkin_view
from view_rewards import create_rewards_view  # 🌟 新增：导入刚才建好的奖励商城


def main(page: ft.Page):
    # ================= [窗口基础设置] =================
    page.title = "吐温自省"
    page.window_width = 400
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = ft.padding.only(top=45, left=15, right=15, bottom=10)

    # ================= [四大容器初始化] =================
    calendar_container, update_calendar_fn = create_calendar_view(page)
    checkin_container = create_checkin_view(page, on_submit_success=update_calendar_fn)
    rewards_container, update_rewards_fn = create_rewards_view(page)  # 🌟 初始化商城容器和刷新函数

    stats_container = ft.Column(controls=[], scroll="adaptive", expand=True, visible=False)

    # ================= [导航与页面切换逻辑] =================
    def switch_tab(e, index):
        # 先把所有页面隐藏
        checkin_container.visible = False
        stats_container.visible = False
        calendar_container.visible = False
        rewards_container.visible = False  # 🌟 隐藏商城

        # 再根据点击的按钮显示对应页面
        if index == 0:
            checkin_container.visible = True
        elif index == 1:
            stats_container.controls = load_stats_ui()
            stats_container.visible = True
        elif index == 2:
            update_calendar_fn()
            calendar_container.visible = True
        elif index == 3:
            update_rewards_fn()  # 🌟 每次点进商城，都重新算一遍积分（防止你刚打完卡分数没变）
            rewards_container.visible = True
        page.update()

    main_content = ft.Column(
        controls=[checkin_container, stats_container, calendar_container, rewards_container],  # 🌟 把商城塞进主画框
        expand=True
    )

    # ================= [底部导航栏扩充为 4 个按钮] =================
    bottom_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.FilledTonalButton(content=ft.Text("📝打卡", size=13), on_click=lambda e: switch_tab(e, 0),
                                     expand=True, height=45),
                ft.FilledTonalButton(content=ft.Text("📊统计", size=13), on_click=lambda e: switch_tab(e, 1),
                                     expand=True, height=45),
                ft.FilledTonalButton(content=ft.Text("📅日历", size=13), on_click=lambda e: switch_tab(e, 2),
                                     expand=True, height=45),
                ft.FilledTonalButton(content=ft.Text("🎁奖励", size=13), on_click=lambda e: switch_tab(e, 3),
                                     expand=True, height=45),  # 🌟 新增的商城入口！
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            spacing=3
        ),
        padding=5,
        bgcolor="#f3f4f6",
        border_radius=10
    )

    page.add(main_content, bottom_bar)
    update_calendar_fn()


ft.run(main)
