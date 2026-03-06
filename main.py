import flet as ft
import sqlite3
from datetime import date
import calendar


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
    page.window_width = 400
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT

    # 🌟 核心修复：增加手机顶部安全距离，防止被刘海/状态栏遮挡！
    page.padding = ft.padding.only(top=45, left=15, right=15, bottom=10)

    # ================= [页面 1] 打卡界面的所有控件 =================
    checkin_title = ft.Text("吐温自省 - 今日打卡", size=24, weight="bold")  # 缩小标题
    date_input = ft.TextField(label="打卡日期 (修改此处可进行历史补签)", value=str(date.today()), width=280)  # 缩小宽度

    def create_time_counter(label_text, step=0.5):
        txt_number = ft.TextField(value="0", text_align="center", width=60, keyboard_type="number")  # 缩小数字框

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
            ft.Text(label_text, width=100, weight="bold", size=14),  # 缩小文字
            ft.FilledTonalButton(content=ft.Text("-", size=18), on_click=minus_click, width=45),
            txt_number,
            ft.FilledTonalButton(content=ft.Text("+", size=18), on_click=plus_click, width=45)
        ], alignment=ft.MainAxisAlignment.START)
        return row, txt_number

    study_row, study_input = create_time_counter("学习时间 (h):", step=0.5)
    research_row, research_input = create_time_counter("科研时间 (h):", step=0.5)

    call_parents_dropdown = ft.Dropdown(
        label="给父母&🌽打电话", value="0", width=160,
        options=[ft.dropdown.Option(str(i)) for i in range(4)]
    )

    fitness_check = ft.Checkbox(label="今日是否健身(+10)", value=False)
    basketball_check = ft.Checkbox(label="今日是否打球(+10)", value=False)
    sleep_check = ft.Checkbox(label="早睡早起 (+10 / -10)", value=False)
    diet_check = ft.Checkbox(label="饮食健康 (+10 / -10)", value=False)
    porn_check = ft.Checkbox(label="未触碰黄色 (违规扣50分)", value=True)

    expense_input = ft.TextField(label="今日花销总额 (元) [≤25加分]", value="0", width=280, keyboard_type="number")
    result_text = ft.Text(size=16, weight="bold", color="blue")

    def submit_data(e):
        try:
            record_date = date_input.value.strip()

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

            msg = f"{record_date} 打卡成功！花销 {expense_amt}元"
            result_text.value = f"{msg}\n单日得分：{score} 分"
            result_text.color = "blue"

            update_calendar()
            page.update()

        except ValueError:
            result_text.value = "请检查数字格式是否正确！"
            result_text.color = "red"
            page.update()

    submit_btn = ft.FilledButton(content=ft.Text("提交数据"), on_click=submit_data, width=280)

    # ================= [页面 2] 核心：动态读取数据库生成统计与奖励 =================
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
                ft.Text("📈 近7天战报", size=24, weight="bold"),  # 缩小标题

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

    # ================= [页面 3] 🌟 史诗级新功能：历史日历 =================

    cal_year_dd = ft.Dropdown(
        options=[ft.dropdown.Option(str(y)) for y in range(2025, 2031)],
        value=str(date.today().year), width=90, height=45, content_padding=5  # 缩小
    )
    cal_month_dd = ft.Dropdown(
        options=[ft.dropdown.Option(str(m)) for m in range(1, 13)],
        value=str(date.today().month), width=70, height=45, content_padding=5  # 缩小
    )

    cal_board_container = ft.Container(alignment=ft.Alignment.CENTER)
    cal_details_container = ft.Container(alignment=ft.Alignment.CENTER)

    def show_day_details(d_str):
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM records WHERE date=?", (d_str,))
        row = cursor.fetchone()

        if row:
            new_content = ft.Container(
                content=ft.Column([
                    ft.Text(f"📅 {d_str} 档案", size=18, weight="bold", color="white"),
                    ft.Divider(color="white"),
                    ft.Text(f"🏆 得分: {row[11]} 分", size=16, weight="bold", color="#ffed4a"),
                    ft.Text(f"📚 学习: {row[1]}h | 🔬 科研: {row[2]}h", color="white", size=13),
                    ft.Text(f"🏋️ 健身: {'是' if row[3] else '否'} | 🏀 打球: {'是' if row[4] else '否'}", color="white",
                            size=13),
                    ft.Text(f"📞 电话: {row[5]}次 | 💰 花销: {row[8]}元", color="white", size=13),
                    ft.Text(f"💤 早睡: {'是' if row[6] else '否'} | 🥗 饮食: {'好' if row[7] else '差'}", color="white",
                            size=13),
                    ft.Text(f"🚫 坚守底线: {'是' if row[10] else '否'}", color="white", size=13),
                ]),
                padding=15,
                bgcolor="#3b82f6",
                border_radius=10,
                width=350
            )
        else:
            new_content = ft.Text(f"📅 {d_str} 没有记录哦！", color="grey", size=14)

        cal_details_container.content = new_content
        try:
            cal_details_container.update()
        except:
            page.update()

    def update_calendar(e=None):
        y = int(cal_year_dd.value)
        m = int(cal_month_dd.value)

        cursor = db_conn.cursor()
        cursor.execute("SELECT date FROM records WHERE date LIKE ?", (f"{y}-{m:02d}-%",))
        db_dates = [row[0] for row in cursor.fetchall()]

        # 🌟 日历格子大瘦身！间距改成 3
        main_col = ft.Column(spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        header_row = ft.Row(spacing=3, alignment=ft.MainAxisAlignment.CENTER)
        for wd in weekdays:
            # 头部文字框也等比例缩小
            header_row.controls.append(
                ft.Container(content=ft.Text(wd, weight="bold", color="grey", size=14), width=36, height=36,
                             alignment=ft.Alignment.CENTER)
            )
        main_col.controls.append(header_row)

        matrix = calendar.monthcalendar(y, m)
        for week in matrix:
            week_row = ft.Row(spacing=3, alignment=ft.MainAxisAlignment.CENTER)
            for day in week:
                if day == 0:
                    week_row.controls.append(ft.Container(width=36, height=36))
                else:
                    date_str = f"{y}-{m:02d}-{day:02d}"
                    has_record = date_str in db_dates
                    bg_color = "#10b981" if has_record else "#f3f4f6"
                    text_color = "white" if has_record else "black"

                    # 🌟 每一天的格子缩小到 36x36
                    btn = ft.Container(
                        content=ft.Text(str(day), color=text_color, weight="bold", size=14),
                        width=36, height=36,
                        bgcolor=bg_color,
                        border_radius=8,
                        alignment=ft.Alignment.CENTER,
                        ink=True,
                        on_click=lambda e, d=date_str: show_day_details(d)
                    )
                    week_row.controls.append(btn)
            main_col.controls.append(week_row)

        cal_board_container.content = main_col
        if e is not None:
            cal_details_container.content = ft.Container()

        try:
            cal_board_container.update()
            cal_details_container.update()
        except:
            page.update()

    # ================= 4. 终极页面架构 (使用可见性切换) =================
    checkin_container = ft.Column(
        controls=[
            checkin_title,
            date_input,
            ft.Divider(),
            study_row, research_row, ft.Divider(),
            ft.Row([fitness_check, basketball_check]),
            call_parents_dropdown, expense_input, ft.Divider(),
            sleep_check, diet_check, porn_check, ft.Divider(),
            submit_btn, result_text
        ],
        scroll="adaptive", expand=True, visible=True
    )

    stats_container = ft.Column(
        controls=[], scroll="adaptive", expand=True, visible=False
    )

    calendar_container = ft.Column(
        controls=[
            ft.Text("岁月史书", size=24, weight="bold"),
            ft.Row([
                cal_year_dd, ft.Text("年", size=16, weight="bold"),
                cal_month_dd, ft.Text("月", size=16, weight="bold"),
                ft.FilledTonalButton(content="🔄", on_click=update_calendar, width=60)  # 刷新按钮变小巧
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(),
            cal_board_container,
            ft.Divider(),
            cal_details_container
        ],
        scroll="adaptive", expand=True, visible=False
    )

    def switch_tab(e, index):
        checkin_container.visible = False
        stats_container.visible = False
        calendar_container.visible = False

        if index == 0:
            checkin_container.visible = True
        elif index == 1:
            stats_container.controls = load_stats_ui()
            stats_container.visible = True
        elif index == 2:
            update_calendar()
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

    page.add(main_content, bottom_bar)
    update_calendar()


ft.run(main)
