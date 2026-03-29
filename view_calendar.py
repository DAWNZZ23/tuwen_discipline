import flet as ft
import calendar
from datetime import date
from database import db_conn  # 🌟 借用数据库钥匙


def create_calendar_view(page: ft.Page):
    cal_year_dd = ft.Dropdown(
        options=[ft.dropdown.Option(str(y)) for y in range(2025, 2031)],
        value=str(date.today().year), width=90, height=45, content_padding=5
    )
    cal_month_dd = ft.Dropdown(
        options=[ft.dropdown.Option(str(m)) for m in range(1, 13)],
        value=str(date.today().month), width=70, height=45, content_padding=5
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

        main_col = ft.Column(spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        header_row = ft.Row(spacing=3, alignment=ft.MainAxisAlignment.CENTER)
        for wd in weekdays:
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

    calendar_container = ft.Column(
        controls=[
            ft.Text("📆岁月史书", size=24, weight="bold"),
            ft.Row([
                cal_year_dd, ft.Text("年", size=16, weight="bold"),
                cal_month_dd, ft.Text("月", size=16, weight="bold"),
                ft.FilledTonalButton(content="🔄", on_click=update_calendar, width=60)
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(),
            cal_board_container,
            ft.Divider(),
            cal_details_container
        ],
        scroll="adaptive", expand=True, visible=False
    )

    # 🌟 核心：不仅返回构建好的日历UI，还把刷新日历的函数也一起打包返回给主程序！
    return calendar_container, update_calendar
