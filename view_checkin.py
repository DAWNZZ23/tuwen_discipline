import flet as ft
from datetime import date
from database import db_conn  # 🌟 拿数据库钥匙


def create_checkin_view(page: ft.Page, on_submit_success):
    # 这里的 on_submit_success 是一个回调函数，用来在打卡成功后通知日历刷新

    checkin_title = ft.Text("吐温自省 - 今日打卡", size=24, weight="bold")
    date_input = ft.TextField(label="打卡日期 (修改此处可进行历史补签)", value=str(date.today()), width=280)

    def create_time_counter(label_text, step=0.5):
        txt_number = ft.TextField(value="0", text_align="center", width=60, keyboard_type="number")

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
            ft.Text(label_text, width=100, weight="bold", size=14),
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

            # 🌟 触发传入的外部函数（刷新日历）
            if on_submit_success:
                on_submit_success()
            page.update()

        except ValueError:
            result_text.value = "请检查数字格式是否正确！"
            result_text.color = "red"
            page.update()

    submit_btn = ft.FilledButton(content=ft.Text("提交数据"), on_click=submit_data, width=280)

    # 将打卡页面的所有控件打包进一个容器中返回
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

    return checkin_container