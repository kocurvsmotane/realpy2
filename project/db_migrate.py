import sqlite3
from datetime import datetime

from _config import DATABASE_PATH
from views import db

__author__ = 'kot'

with sqlite3.connect(DATABASE_PATH) as conn:
    c = conn.cursor()

    # temporarily change the name of tasks table
    c.execute("""ALTER TABLE tasks RENAME TO old_tasks""")

    # recreate a new tasks table with updated schema
    db.create_all()

    # retrieve data from old_tasks table
    c.execute("""SELECT  name, due_date, priority, status FROM old_tasks ORDER BY task_id ASC""")

    # save all rows as a list of tuples; set posted_date to now and user_id to 1
    data = [(r[0], r[1], r[2], r[3], datetime.now(), 1) for r in c.fetchall()]

    # insert data to tasks table
    c.executemany("""INSERT INTO tasks (name, due_date, priority, status, posted_date, user_id) VALUES (?, ?, ?, ?, ?, ?)""", data)

    # delete old_tasks table
    c.execute("""DROP TABLE old_tasks""")
