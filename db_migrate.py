import sqlite3

from project._config import DATABASE_PATH
from project import db

__author__ = 'kot'

with sqlite3.connect(DATABASE_PATH) as conn:
    c = conn.cursor()

    # temporarily change the name of tasks table
    c.execute("""ALTER TABLE users RENAME TO old_users""")

    # recreate a new tasks table with updated schema
    db.create_all()

    # retrieve data from old_tasks table
    c.execute("""SELECT name, email, password FROM old_users ORDER BY id ASC""")

    # save all rows as a list of tuples; set posted_date to now and user_id to 1
    data = [(r[0], r[1], r[2], 'user') for r in c.fetchall()]

    # insert data to tasks table
    c.executemany("""INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)""", data)

    # delete old_tasks table
    c.execute("""DROP TABLE old_users""")
