from datetime import date

from project.models import Task, User
from project import db

__author__ = 'kot'

# create the database and the db table
db.create_all()

# insert data
db.session.add(User('admin', 'ad@min.com', 'admin', 'admin'))
db.session.add(Task("Finish this tutorial", date(2019, 9, 22), 10, date(2019, 2, 11), 1, 1))
db.session.add(Task("Finish Real Python Course 2", date(2019, 10, 3), 10, date(2019, 2, 11), 1, 1))

# commit the changes
db.session.commit()
