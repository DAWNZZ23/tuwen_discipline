import sqlite3

# ================= 1. 数据库模块 =================
def init_db():
    conn = sqlite3.connect('discipline.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS records
                   (
                       date TEXT PRIMARY KEY,
                       study_hours REAL,
                       research_hours REAL,
                       fitness_count INTEGER,
                       basketball_count INTEGER,
                       call_parents INTEGER,
                       sleep_early INTEGER,
                       diet_healthy INTEGER,
                       expense_amount REAL,
                       expense_reasonable INTEGER,
                       porn_avoided INTEGER,
                       daily_score INTEGER
                   )
                   ''')
    conn.commit()
    return conn

# 暴露出一个全局的数据库连接对象
db_conn = init_db()