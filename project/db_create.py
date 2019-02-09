import sqlite3
from _config import DATABASE_PATH

__author__ = 'kot'

with sqlite3.connect(DATABASE_PATH) as conn:
    c = conn.cursor()

    # create the table
    c.execute("""CREATE TABLE tasks
                (task_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, due_date TEXT NOT NULL,
                priority INTERGER NOT NULL, status INTEGER NOT NULL)""")

    # insert dummy data into the table
    c.execute('INSERT INTO tasks (name, due_date, priority, status) VALUES'
              '("Finish this tutorial", "03/25/2019", 10, 1)')
    c.execute('INSERT INTO tasks (name, due_date, priority, status) VALUES'
              '("Finish Real Python Course 2", "03/25/2019", 10, 1)')
