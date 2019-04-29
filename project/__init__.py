import datetime

from flask import Flask, render_template, request
from flask_bcrypt import Bcrypt
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('_config.py')
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
api_flask = Api(app)

from project.users.views import users_blueprint
from project.tasks.views import tasks_blueprint
from project.api.views import api_blueprint
from project.api.api_flask import TaskApi, TasksApi

# register our blueprints
app.register_blueprint(users_blueprint)
app.register_blueprint(tasks_blueprint)
app.register_blueprint(api_blueprint)

# register flask-restful endpoint
api_flask.add_resource(TasksApi, '/api/v2/tasks/')
api_flask.add_resource(TaskApi, '/api/v2/tasks/<int:task_id>/')


@app.errorhandler(404)
def not_found(error):
    if app.debug is not True:
        now = datetime.datetime.now()
        r = request.url
        with open('error.log', 'a') as f:
            current_timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
            f.write(f"\n404 error at {current_timestamp}: {r}")
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if app.debug is not True:
        now = datetime.datetime.now()
        r = request.url
        with open('error.log', 'a') as f:
            current_timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
            f.write(f"\n500 error at {current_timestamp}: {r}")
    return render_template('500.html'), 500
