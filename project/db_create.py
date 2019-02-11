from datetime import date

from models import Task
from views import db

__author__ = 'kot'

# create the database and the db table
db.create_all()

# insert data
db.session.add(Task("Finish this tutorial", date(2019, 9, 22), 10, 1))
db.session.add(Task("Finish Real Python Course 2", date(2019, 10, 3), 10, 1))

# commit the changes
db.session.commit()
