import sqlite3
# Создание БД и пустой таблицы с полями.
con = sqlite3.connect(r'db/users.db')
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(
   user_id TEXT,
   rating TEXT,
   comment TEXT,
   time INT);
""")
con.commit()