import flet as ft
from database import db_conn
from datetime import datetime


def create_rewards_view(page: ft.Page):
    main_container = ft.Column(scroll="adaptive", expand=True, visible=False)

    def update_ui(msg="", msg_color="blue"):
        main_container.controls.clear()

        cursor = db_conn.cursor()

        # 1. 获取所有的历史总得分
        cursor.execute("SELECT SUM(daily_score) FROM records")
        res = cursor.fetchone()
        total_earned = res[0] if res and res[0] else 0

        # 2. 获取所有的历史总消费
        cursor.execute("SELECT SUM(cost) FROM spent_points")
        res_spent = cursor.fetchone()
        total_spent = res_spent[0] if res_spent and res_spent[0] else 0

        # 3. 算出当前可用积分！
        current_points = total_earned - total_spent

        # ================= 顶部积分看板 =================
        header = ft.Row(
            [
                ft.Text("🎁 积分商城", size=24, weight="bold"),
                ft.Container(
                    content=ft.Row([
                        ft.Text("⭐️", size=18),
                        ft.Text(f"可用积分: {current_points}", size=18, weight="bold", color="#d97706")
                    ]),
                    bgcolor="#fef3c7", padding=10, border_radius=10
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        # 交互反馈文字（成功或失败提示）
        msg_area = ft.Text(msg, color=msg_color, weight="bold", size=14)

        # ================= 兑换响应函数 =================
        def redeem_item(item_name, cost):
            if current_points >= cost:
                # 扣分，写进记账本
                c = db_conn.cursor()
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO spent_points (item_name, cost, redeem_time) VALUES (?, ?, ?)",
                          (item_name, cost, now_str))
                db_conn.commit()
                # 刷新界面并提示成功
                update_ui(f"🎉 成功兑换：{item_name}！扣除 {cost} 积分", "green")
            else:
                # 刷新界面并提示失败
                update_ui(f"❌ 积分不足！兑换 {item_name} 还差 {cost - current_points} 分", "red")

        # ================= 🌟 扩充版商品列表 =================
        # 根据日均 110 分精心设计的阶梯物价
        rewards_catalog = [
            # 🔵 微小确幸 (1-2天可兑换)

            {"name": "🧋 酸奶畅享", "cost": 150, "desc": "奖励自己一杯美味酸奶 "},
            {"name": "🛌 周末睡个大懒觉", "cost": 250, "desc": "关掉闹钟，睡到自然醒的特权 "},

            # 🟢 周末放纵 (3-7天可兑换)
            {"name": "🍜 食堂豪华面", "cost": 350, "desc": "加荤加蛋加满料，吃顿好的！"},
            {"name": "🎞️电影一场", "cost": 400, "desc": "彻底放空！"},
            {"name": "🎮 游戏畅玩一晚上", "cost": 400, "desc": "毫无负罪感地打游戏，谁也别管我 "},

            {"name": "🥩 外卖任意一顿", "cost": 800, "desc": "狠狠搓一顿好的 "},
            {"name": "🍗 KFC/麦当劳大餐", "cost": 1000, "desc": "疯狂星期四，或者周末放纵一下 "},
            # 🟡 月度小目标 (10-30天可兑换)
            {"name": "🥘 自助走起", "cost": 1500, "desc": "疯狂星期四，或者周末放纵一下 "},
            # 🔴 终极自律大奖 (长期坚持)
            {"name": "😊 买个想要的东西", "cost": 4000, "desc": "钱不花就是废纸一张 "},

            {"name": "✈️ 来一次旅行", "cost": 8000, "desc": "去个远方，见识更大的世界 "},
        ]

        grid = ft.Column(spacing=10)
        for item in rewards_catalog:
            # 判断积分是否够，够的话按钮是绿色的，不够就是灰色的
            can_afford = current_points >= item['cost']
            btn_color = "#10b981" if can_afford else "grey"

            grid.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(item["name"], size=16, weight="bold"),
                            ft.Text(item["desc"], size=12, color="grey")
                        ], expand=True),
                        ft.FilledTonalButton(
                            content=ft.Text(f"{item['cost']} 分", color="white"),
                            on_click=lambda e, n=item["name"], c=item["cost"]: redeem_item(n, c),
                            style=ft.ButtonStyle(bgcolor=btn_color)
                        )
                    ]),
                    padding=15, border=ft.border.all(1, "#e5e7eb"), border_radius=10
                )
            )

        # ================= 兑换历史 =================
        cursor.execute("SELECT item_name, cost, redeem_time FROM spent_points ORDER BY id DESC LIMIT 10")
        history_rows = cursor.fetchall()

        history_list = ft.Column(spacing=5)
        if history_rows:
            for row in history_rows:
                history_list.controls.append(
                    ft.Text(f"🛒 {row[2][:10]} | 兑换 {row[0]} (-{row[1]}分)", size=13, color="grey")
                )
        else:
            history_list.controls.append(ft.Text("暂无兑换记录", size=13, color="grey"))

        # ================= 组装界面 =================
        main_container.controls.extend([
            header,
            msg_area,
            ft.Divider(),
            ft.Text("🛒 可兑换奖励", weight="bold", size=16),
            grid,
            ft.Divider(),
            ft.Text("📜 最近兑换记录", weight="bold", size=16),
            history_list
        ])

        try:
            main_container.update()
        except:
            page.update()

    update_ui()
    # 返回容器本身和它的刷新函数
    return main_container, update_ui
