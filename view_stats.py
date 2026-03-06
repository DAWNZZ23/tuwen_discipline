import flet as ft
from database import db_conn # 🌟 向 database.py 借用数据库钥匙！

def load_stats_ui():
    try:
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM records ORDER BY date DESC LIMIT 7")
        rows = cursor.fetchall()

        if not rows:
            return [ft.Text("暂无打卡数据，快去打卡吧！", color="grey", size=16)]

        def safe_get(row, index):
            if index < len(row) and row[index] is not None:
                return row[index]
            return 0

        total_score = sum(safe_get(row, 11) for row in rows)
        total_study = sum(safe_get(row, 1) for row in rows)
        total_research = sum(safe_get(row, 2) for row in rows)
        total_fitness = sum(safe_get(row, 3) for row in rows)
        total_expense = sum(safe_get(row, 8) for row in rows)

        reward_title = ""
        reward_desc = ""
        reward_color = "black"

        if total_score >= 900:
            reward_title = "👑 满级大佬"
            reward_desc = "当前解锁：畅玩游戏！你这周简直是神！"
            reward_color = "#d97706"
        elif total_score >= 700:
            reward_title = "🍗 黄金段位"
            reward_desc = f"当前解锁：KFC！ (差 {900 - total_score} 分升级)"
            reward_color = "#b91c1c"
        elif total_score >= 500:
            reward_title = "🍜 白银段位"
            reward_desc = f"当前解锁：豪华面！ (差 {700 - total_score} 分升级)"
            reward_color = "#0369a1"
        elif total_score >= 300:
            reward_title = "🥤 青铜段位"
            reward_desc = f"当前解锁：酸奶杯！ (差 {500 - total_score} 分升级)"
            reward_color = "#15803d"
        else:
            reward_title = "🌱 新手村"
            reward_desc = f"暂无奖励 (差 {300 - total_score} 分拿酸奶杯)"
            reward_color = "#4b5563"

        content = [
            ft.Text("📈 近7天战报", size=24, weight="bold"),

            ft.Container(
                content=ft.Column([
                    ft.Text("🎁 本周战利品", size=16, weight="bold", color="white"),
                    ft.Text(reward_title, size=20, weight="bold", color="white"),
                    ft.Text(reward_desc, size=13, color="white"),
                ]),
                padding=15,
                bgcolor=reward_color,
                border_radius=10,
                width=350
            ),
            ft.Divider(height=10, color="transparent"),

            ft.Container(
                content=ft.Column([
                    ft.Text(f"🏆 累计得分: {total_score} 分", size=20, weight="bold", color="green"),
                    ft.Divider(color="white"),
                    ft.Text(f"📚 学习: {total_study} h | 🔬 科研: {total_research} h", size=14),
                    ft.Text(f"🏃 汗水: {total_fitness} 天 | 💰 花销: {total_expense} 元", size=14),
                ]),
                padding=20,
                bgcolor="#e0f2fe",
                border_radius=15,
                width=350
            ),
            ft.Divider(),
            ft.Text("📅 历史打卡明细:", weight="bold", size=16)
        ]

        for row in sorted(rows, key=lambda x: x[0]):
            date_str = row[0] if len(row) > 0 else "未知日期"
            score = safe_get(row, 11)
            expense = safe_get(row, 8)
            content.append(ft.Text(f"{date_str} | 得分:{score} | 花销:{expense}元", size=14))

        return content

    except Exception as e:
        return [
            ft.Text("⚠️ 数据读取出错！", color="red", size=18, weight="bold"),
        ]