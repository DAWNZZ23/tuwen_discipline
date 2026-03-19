import sqlite3


def init_db():
    conn = sqlite3.connect('discipline.db', check_same_thread=False)
    cursor = conn.cursor()

    # 你的历史打卡表（原封不动）
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

    # 🌟 新增：用于记录花费积分的表
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS spent_points
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       item_name
                       TEXT,
                       cost
                       INTEGER,
                       redeem_time
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   ''')
    conn.commit()
    return conn


db_conn = init_db()
