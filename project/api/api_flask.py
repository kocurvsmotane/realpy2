from flask import jsonify, session, request
from flask_restful import Resource, abort, reqparse
from datetime import datetime

from project import db
from project.models import Task

__author__ = 'kot'

parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True)
parser.add_argument('due_date', type=lambda x: datetime.strptime(x, '%Y-%m-%d'), required=True)
parser.add_argument('priority', type=int, required=True, choices=[x for x in range(1, 11)])
parser.add_argument('status', type=int, required=False, choices=(0, 1))


class TasksApi(Resource):
    # return last tasks
    def get(self):
        result = db.session.query(Task).limit(10).offset(0).all()
        tasks = [{
            'task_id': r.task_id,
            'task_name': r.name,
            'due_date': str(r.due_date),
            'priority': r.priority,
            'posted_date': str(r.posted_date),
            'status': r.status,
            'user_id': r.user_id
        } for r in result]
        return jsonify(tasks)

    # post a new task
    def post(self):
        req = parser.parse_args(strict=True)
        req = {k: v for k, v in req.items() if v is not None}
        if not session.get('user_id'):
            abort(401, message="You have to authorize first.")
        task = Task(req['name'], req['due_date'], req['priority'], datetime.utcnow(), '1', session['user_id'])
        db.session.add(task)
        db.session.commit()
        return 'New entry was successfully posted. Thanks.'


class TaskApi(Resource):
    # return a task by id
    def get(self, task_id):
        result = db.session.query(Task).filter_by(task_id=task_id).first()
        if not result:
            return abort(404, message=f"Task {task_id} doesn't exist")
        task = {
            'task_id': result.task_id,
            'task_name': result.name,
            'due_date': str(result.due_date),
            'priority': result.priority,
            'posted_date': str(result.posted_date),
            'status': result.status,
            'user_id': result.user_id
        }
        return jsonify(task)

    # delete a task
    def delete(self, task_id):
        result = db.session.query(Task).filter_by(task_id=task_id)
        if not result.first():
            return abort(404, message=f"Task {task_id} doesn't exist")
        if session.get('user_id') == result.first().user_id or session['role'] == 'admin':
            result.delete()
            db.session.commit()
        else:
            abort(403, message="You can only delete tasks that belong to you.")

    # edit a task
    def put(self, task_id):
        task = db.session.query(Task).filter_by(task_id=task_id)
        if not task.first():
            return abort(404, message=f"Task {task_id} doesn't exist")
        if session.get('user_id') == task.first().user_id or session['role'] == 'admin':
            req = parser.parse_args(strict=True)
            req = {k: v for k, v in req.items() if v is not None}  # removing all the Nones
            task.update(req)
            db.session.commit()
            return jsonify(task)
        else:
            abort(403, message="You can only edit tasks that belong to you.")
