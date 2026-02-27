import flet as ft
import sqlite3
from datetime import date


# ================= 1. 数据库模块 =================
def init_db():
    conn = sqlite3.connect('discipline.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS records
                   (
                       date
                       TEXT
                       PRIMARY
                       KEY,
                       study_hours
                       REAL,
                       research_hours
                       REAL,
                       fitness_count
                       INTEGER,
                       basketball_count
                       INTEGER,
                       call_parents
                       INTEGER,
                       sleep_early
                       INTEGER,
                       diet_healthy
                       INTEGER,
                       expense_amount
                       REAL,
                       expense_reasonable
                       INTEGER,
                       porn_avoided
                       INTEGER,
                       daily_score
                       INTEGER
                   )
                   ''')
    conn.commit()
    return conn


db_conn = init_db()


# ================= 2. 界面与交互模块 =================
def main(page: ft.Page):
    page.title = "吐温自省"
    page.window_width = 450
    page.window_height = 850
    page.theme_mode = ft.ThemeMode.LIGHT

    # ================= [页面 1] 打卡界面的所有控件 =================
    checkin_title = ft.Text("吐温自省 - 今日打卡", size=28, weight="bold")

    def create_time_counter(label_text, step=0.5):
        txt_number = ft.TextField(value="0", text_align="center", width=80, keyboard_type="number")

        def minus_click(e):
            val = float(txt_number.value)
            if val >= step:
                txt_number.value = str(round(val - step, 1))
                txt_number.update()

        def plus_click(e):
            val = float(txt_number.value)
            txt_number.value = str(round(val + step, 1))
            txt_number.update()

        row = ft.Row([
            ft.Text(label_text, width=120, weight="bold"),
            ft.FilledTonalButton(content=" - ", on_click=minus_click),
            txt_number,
            ft.FilledTonalButton(content=" + ", on_click=plus_click)
        ], alignment=ft.MainAxisAlignment.START)
        return row, txt_number

    study_row, study_input = create_time_counter("学习时间 (h):", step=0.5)
    research_row, research_input = create_time_counter("科研时间 (h):", step=0.5)

    call_parents_dropdown = ft.Dropdown(
        label="给父母&🌽打电话次数", value="0", width=200,
        options=[ft.dropdown.Option(str(i)) for i in range(4)]
    )

    fitness_check = ft.Checkbox(label="今日是否健身 (+10)", value=False)
    basketball_check = ft.Checkbox(label="今日是否打球 (+10)", value=False)
    sleep_check = ft.Checkbox(label="早睡早起 (+10 / -10)", value=False)
    diet_check = ft.Checkbox(label="饮食健康 (+10 / -10)", value=False)
    porn_check = ft.Checkbox(label="未触碰黄色 (坚守底线! 违规扣50分)", value=True)

    expense_input = ft.TextField(label="今日花销总额 (元) [≤25元加分]", value="0", width=300, keyboard_type="number")
    result_text = ft.Text(size=20, weight="bold", color="blue")

    def submit_data(e):
        try:
            # 自动获取今天的真实日期
            record_date = str(date.today())

            study = float(study_input.value)
            research = float(research_input.value)
            fitness = 1 if fitness_check.value else 0
            basketball = 1 if basketball_check.value else 0
            call = int(call_parents_dropdown.value)
            sleep = sleep_check.value
            diet = diet_check.value
            porn = porn_check.value

            expense_amt = float(expense_input.value)
            expense_reasonable = True if expense_amt <= 25 else False

            score = 0
            score += int(study * 10) + int(research * 10)
            score += fitness * 10 + basketball * 10 + call * 10
            score += 10 if sleep else -10
            score += 10 if diet else -10
            score += 10 if expense_reasonable else -10
            if porn:
                score += 10
            else:
                score -= 50

            cursor = db_conn.cursor()
            cursor.execute('''
                           INSERT INTO records
                           (date, study_hours, research_hours, fitness_count, basketball_count, call_parents,
                            sleep_early, diet_healthy, expense_amount, expense_reasonable, porn_avoided, daily_score)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(date) DO
                           UPDATE SET
                               study_hours=excluded.study_hours, research_hours=excluded.research_hours,
                               fitness_count=excluded.fitness_count, basketball_count=excluded.basketball_count,
                               call_parents=excluded.call_parents, sleep_early=excluded.sleep_early,
                               diet_healthy=excluded.diet_healthy, expense_amount=excluded.expense_amount,
                               expense_reasonable=excluded.expense_reasonable,
                               porn_avoided=excluded.porn_avoided, daily_score=excluded.daily_score
                           ''', (record_date, study, research, fitness, basketball, call, sleep, diet, expense_amt,
                                 int(expense_reasonable), porn, score))
            db_conn.commit()

            msg = f"打卡成功！今日花销 {expense_amt}元 ({'达标+10' if expense_reasonable else '超标-10'})"
            result_text.value = f"{msg}\n单日得分：{score} 分"
            result_text.color = "blue"
            page.update()

        except ValueError:
            result_text.value = "请检查数字格式是否正确！"
            result_text.color = "red"
            page.update()

    submit_btn = ft.FilledButton(content="提交打卡数据", on_click=submit_data, width=300)

    # ================= [页面 2] 核心：动态读取数据库生成统计与奖励 =================
    def load_stats_ui():
        try:
            cursor = db_conn.cursor()
            cursor.execute("SELECT * FROM records ORDER BY date DESC LIMIT 7")
            rows = cursor.fetchall()

            if not rows:
                return [ft.Text("暂无打卡数据，快去首页打卡吧！", color="grey", size=16)]

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
                reward_desc = f"当前解锁：KFC！ (距【畅玩游戏】还差 {900 - total_score} 分)"
                reward_color = "#b91c1c"
            elif total_score >= 500:
                reward_title = "🍜 白银段位"
                reward_desc = f"当前解锁：食堂豪华面！ (距【KFC】还差 {700 - total_score} 分)"
                reward_color = "#0369a1"
            elif total_score >= 300:
                reward_title = "🥤 青铜段位"
                reward_desc = f"当前解锁：酸奶杯！ (距【食堂豪华面】还差 {500 - total_score} 分)"
                reward_color = "#15803d"
            else:
                reward_title = "🌱 新手村"
                reward_desc = f"暂无奖励 (距最低奖励【酸奶杯】还差 {300 - total_score} 分，冲鸭！)"
                reward_color = "#4b5563"

            content = [
                ft.Text("📈 近7天自律战报", size=28, weight="bold"),

                ft.Container(
                    content=ft.Column([
                        ft.Text("🎁 本周战利品", size=18, weight="bold", color="white"),
                        ft.Text(reward_title, size=24, weight="bold", color="white"),
                        ft.Text(reward_desc, size=14, color="white"),
                    ]),
                    padding=15,
                    bgcolor=reward_color,
                    border_radius=10,
                    width=400
                ),
                ft.Divider(height=10, color="transparent"),

                ft.Container(
                    content=ft.Column([
                        ft.Text(f"🏆 累计得分: {total_score} 分", size=22, weight="bold", color="green"),
                        ft.Divider(color="white"),
                        ft.Text(f"📚 沉浸学习: {total_study} 小时", size=16),
                        ft.Text(f"🔬 潜心科研: {total_research} 小时", size=16),
                        ft.Text(f"🏃 挥洒汗水: {total_fitness} 天", size=16),
                        ft.Text(f"💰 累计花销: {total_expense} 元", size=16),
                    ]),
                    padding=20,
                    bgcolor="#e0f2fe",
                    border_radius=15,
                    width=400
                ),
                ft.Divider(),
                ft.Text("📅 历史打卡明细:", weight="bold", size=18)
            ]

            # 使用 sorted 进行正序排列
            for row in sorted(rows, key=lambda x: x[0]):
                date_str = row[0] if len(row) > 0 else "未知日期"
                score = safe_get(row, 11)
                expense = safe_get(row, 8)
                content.append(ft.Text(f"{date_str} | 得分: {score} | 花销: {expense}元", size=15))

            return content

        except Exception as e:
            return [
                ft.Text("⚠️ 数据读取出错！", color="red", size=20, weight="bold"),
                ft.Text(f"错误信息: {str(e)}", color="red")
            ]

    # ================= 3. 终极防白屏页面架构 (使用可见性切换) =================
    checkin_container = ft.Column(
        controls=[
            checkin_title,
            ft.Divider(),
            study_row, research_row, ft.Divider(),
            ft.Row([fitness_check, basketball_check]),
            call_parents_dropdown, expense_input, ft.Divider(),
            sleep_check, diet_check, porn_check, ft.Divider(),
            submit_btn, result_text
        ],
        scroll="adaptive",
        expand=True,
        visible=True
    )

    stats_container = ft.Column(
        controls=[],
        scroll="adaptive",
        expand=True,
        visible=False
    )

    def switch_tab(e, index):
        if index == 0:
            checkin_container.visible = True
            stats_container.visible = False
        else:
            stats_container.controls = load_stats_ui()
            checkin_container.visible = False
            stats_container.visible = True
        page.update()

    main_content = ft.Column(
        controls=[checkin_container, stats_container],
        expand=True
    )

    bottom_bar = ft.Container(
        content=ft.Row(
            controls=[
                ft.FilledTonalButton("📝 今日打卡", on_click=lambda e: switch_tab(e, 0), expand=True, height=50),
                ft.FilledTonalButton("📊 数据统计", on_click=lambda e: switch_tab(e, 1), expand=True, height=50),
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY
        ),
        padding=10,
        bgcolor="#f3f4f6",
        border_radius=10
    )

    page.add(main_content, bottom_bar)


ft.app(target=main)
