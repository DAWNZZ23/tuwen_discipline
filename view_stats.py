import flet as ft
from database import db_conn


def load_stats_ui():
    try:
        cursor = db_conn.cursor()

        # 查出出【全部】历史记录！按日期降序（最新在前）
        cursor.execute("SELECT * FROM records ORDER BY date DESC")
        all_rows = cursor.fetchall()

        if not all_rows:
            return [ft.Text("暂无打卡数据，快去打卡吧！", color="grey", size=16)]

        def safe_get(row, index):
            if index < len(row) and row[index] is not None:
                return row[index]
            return 0

        # 1. 计算所有时间的累计数据
        total_score = sum(safe_get(row, 11) for row in all_rows)
        total_study = sum(safe_get(row, 1) for row in all_rows)
        total_research = sum(safe_get(row, 2) for row in all_rows)
        total_fitness = sum(safe_get(row, 3) for row in all_rows)
        total_expense = sum(safe_get(row, 8) for row in all_rows)

        # ================= 🌟 纯手工打造条形图 (带完美对齐魔法) =================
        rows_7_days = all_rows[:7]  # 获取近 7 天
        rows_7_sorted = sorted(rows_7_days, key=lambda x: x[0])  # 时间正序

        max_score = 0
        for row in rows_7_sorted:
            score = safe_get(row, 11)
            if score > max_score:
                max_score = score  # 寻找最高分作为比例尺

        chart_bars = []
        for row in rows_7_sorted:
            date_short = row[0][-5:]  # 截取 03-06
            score = safe_get(row, 11)

            # 计算柱子的动态高度 (最高限制在 80 像素，留出顶部空间)
            bar_h = 0
            if max_score > 0:
                bar_h = int((score / max_score) * 80)

            # 拼装单根柱子
            single_bar = ft.Column(
                controls=[
                    ft.Container(expand=True),  # 🌟 隐形弹簧：自动膨胀，把下面的元素全部往下挤！
                    ft.Text(str(score), size=12, color="#0ea5e9", weight="bold"),  # 顶部悬浮分数
                    ft.Container(
                        width=20,
                        height=bar_h,
                        bgcolor="#3b82f6",  # 蓝色柱子
                        border_radius=5,
                        tooltip=f"{row[0]}: {score}分"
                    ),
                    ft.Text(date_short, size=10, color="black")  # 底部日期
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                height=140  # 固定总高度，配合弹簧实现底部完美对齐
            )
            chart_bars.append(single_bar)

        # 把所有柱子横向一字排开
        custom_bar_chart = ft.Row(
            controls=chart_bars,
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            vertical_alignment=ft.CrossAxisAlignment.END,
            height=150
        )

        # ================= 构筑全部历史记录列表 (ListView) =================
        history_list = ft.ListView(expand=True, spacing=5, height=200)
        for row in all_rows:
            d_str = row[0]
            s = safe_get(row, 11)
            exp = safe_get(row, 8)
            history_list.controls.append(ft.Text(f"{d_str} | 得分:{s} | 花销:{exp}元", size=14))

        # ================= 最终组装界面返回 =================
        return [
            ft.Text("📊 数据中心", size=24, weight="bold"),

            # 1. 累计统计面板
            ft.Container(
                content=ft.Column([
                    ft.Text(f"🏆 累计得分: {total_score} 分", size=20, weight="bold", color="green"),
                    ft.Divider(color="white"),
                    ft.Text(f"📚 学习: {total_study} h | 🔬 科研: {total_research} h", size=14),
                    ft.Text(f"🏃 汗水: {total_fitness} 天 | 💰 花销: {total_expense} 元", size=14),
                ]),
                padding=20, bgcolor="#e0f2fe", border_radius=15, width=350
            ),
            ft.Divider(),

            # 2. 近7天手工条形图
            ft.Text("📈 近7天得分趋势:", weight="bold", size=16),
            ft.Container(
                content=custom_bar_chart,
                padding=10, bgcolor="#fce7f3", border_radius=10, width=350
            ),
            ft.Divider(),

            # 3. 全部历史记录
            ft.Text("📅 全部历史明细 (内部可滑动):", weight="bold", size=16),
            ft.Container(
                content=history_list,
                padding=10, border=ft.border.all(1, "#e5e7eb"), border_radius=10, width=350
            )
        ]

    except Exception as e:
        return [
            ft.Text("⚠️ 数据读取出错！", color="red", size=18, weight="bold"),
            ft.Text(str(e), color="red", size=12)
        ]
