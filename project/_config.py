import os

__author__ = 'kot'

# grab the folder where this script lives
basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

DATABASE = 'flasktaskr.db'
WTF_CSRF_ENABLED = True
SECRET_KEY = b'\xcfD\xe6,%\xda\x90\n\x89?X\x01\xfaYJg\x90e\x1f\x84\x12D\xbf\x03\xad'

# define the full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

# database uri
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
