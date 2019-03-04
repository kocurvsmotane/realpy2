from project import db

__author__ = 'kot'

# create the database and the db table
db.create_all()

# commit the changes
db.session.commit()
