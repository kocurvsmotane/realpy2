import sqlite3
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for, g

from forms import AddTaskForm

__author__ = 'kot'

# config
app = Flask(__name__)
app.config.from_object('_config')


# helper functions

def connect_db():
    return sqlite3.connect(app.config['DATABASE_PATH'])


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


# route handlers

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Goodbye!')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid credentials. Please try again.'
            return render_template('login.html', error=error)
        else:
            session['logged_in'] = True
            flash('Welcome!')
            return redirect(url_for('tasks'))
    return render_template('login.html')


@app.route('/tasks/')
@login_required
def tasks():
    g.db = connect_db()
    cursor = g.db.execute("SELECT name, due_date, priority, task_id FROM tasks WHERE status=1")
    open_tasks = [dict(name=r[0], due_date=r[1], priority=r[2], task_id=r[3]) for r in cursor.fetchall()]
    cursor = g.db.execute("SELECT name, due_date, priority, task_id FROM tasks WHERE status=0")
    closed_tasks = [dict(name=r[0], due_date=r[1], priority=r[2], task_id=r[3]) for r in cursor.fetchall()]
    g.db.close()
    return render_template('tasks.html', form=AddTaskForm(request.form), open_tasks=open_tasks, closed_tasks=closed_tasks)


@app.route('/add/', methods=['POST'])
@login_required
def new_task():
    g.db = connect_db()
    name = request.form['name']
    date = request.form['due_date']
    priority = request.form['priority']
    if not name or not date or not priority:
        flash("All fields are required. Please try again.")
        return redirect(url_for('tasks'))
    else:
        g.db.execute('INSERT INTO tasks (name, due_date, priority, status) VALUES (?, ?, ?, 1)',
                     [request.form['name'], request.form['due_date'], request.form['priority']])
        g.db.commit()
        g.db.close()
        flash('New entry was successfully posted. Thanks.')
        return redirect(url_for('tasks'))


@app.route('/complete/<int:task_id>/')
@login_required
def complete(task_id):
    g.db = connect_db()
    g.db.execute(f'UPDATE tasks SET status=0 WHERE task_id={str(task_id)}')
    g.db.commit()
    g.db.close()
    flash('The task was marked as complete.')
    return redirect(url_for('tasks'))


@app.route('/delete/<int:task_id>/')
@login_required
def delete_entry(task_id):
    g.db = connect_db()
    g.db.execute(f'DELETE FROM tasks WHERE task_id={str(task_id)}')
    g.db.commit()
    g.db.close()
    flash('The task was deleted.')
    return redirect(url_for('tasks'))
