import os
import unittest
from datetime import date

from project._config import basedir
from project import app, db, bcrypt
from project.models import Task, User

TEST_DB = 'test.db'


class TasksTests(unittest.TestCase):

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

        self.assertEqual(app.debug, False)

    # executed after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # helper functions

    def login(self, name, password):
        return self.app.post('/', data=dict(name=name, password=password), follow_redirects=True)

    def register(self, name, email, password, confirm):
        return self.app.post('register/', data=dict(name=name, email=email, password=password, confirm=confirm), follow_redirects=True)

    def logout(self):
        return self.app.get('logout/', follow_redirects=True)

    def create_task(
            self,
            name='Go to the bank',
            due_date='10/08/2016',
            priority='1',
            posted_date='10/08/2016',
            status='1'):
        return self.app.post('add/', data=dict(
            name=name,
            due_date=due_date,
            priority=priority,
            posted_date=posted_date,
            status=status,
        ), follow_redirects=True)

    def create_admin_user(self):
        db.session.add(User('Norris', 'norris@superpower.eu', bcrypt.generate_password_hash('nor'), 'admin'))
        db.session.commit()

    def test_logged_in_users_can_access_tasks_page(self):
        self.register('Fletcher', 'fletcher@realpython.com', 'python101', 'python101')
        self.login('Fletcher', 'python101')
        response = self.app.get('tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add a new task:', response.data)

    def test_not_logged_in_users_cannot_access_tasks_page(self):
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn(b'You need to login first.', response.data)

    def test_users_can_add_tasks(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(b'New entry was successfully posted. Thanks.', response.data)

    def test_users_cannot_add_tasks_when_error(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task(due_date='')
        self.assertIn(b'This field is required.', response.data)

    def test_users_can_complete_tasks(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get('complete/1/', follow_redirects=True)
        self.assertIn(b'The task is complete. Nice.', response.data)

    def test_users_can_delete_tasks(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get('delete/1/', follow_redirects=True)
        self.assertIn(b'The task was deleted.', response.data)

    def test_users_cannot_complete_tasks_that_are_not_created_by_them(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.register('Fletcher', 'fletcher@realpython.com', 'python101', 'python101')
        self.login('Fletcher', 'python101')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get('complete/1/', follow_redirects=True)
        self.assertNotIn(b'The task is complete. Nice.', response.data)
        self.assertIn(b'You can only update tasks that belong to you.', response.data)

    def test_users_cannot_delete_tasks_that_are_not_created_by_them(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.register('Fletcher', 'fletcher@realpython.com', 'python101', 'python101')
        self.login('Fletcher', 'python101')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get('delete/1/', follow_redirects=True)
        self.assertNotIn(b'The task was deleted. Why not add a new one?', response.data)
        self.assertIn(b'You can only delete tasks that belong to you.', response.data)

    def test_admins_can_complete_tasks_that_are_not_created_by_them(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Norris', 'nor')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get('complete/1/', follow_redirects=True)
        self.assertIn(b'The task is complete. Nice.', response.data)
        self.assertNotIn(b'You can only update tasks that belong to you.', response.data)

    def test_admins_can_delete_tasks_that_are_not_created_by_them(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Norris', 'nor')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get('delete/1/', follow_redirects=True)
        self.assertIn(b'The task was deleted. Why not add a new one?', response.data)
        self.assertNotIn(b'You can only delete tasks that belong to you.', response.data)

    def test_string_representation_of_the_task_object(self):
        db.session.add(Task('Check email', date(2019, 2, 22), '1', date(2019, 2, 21), '1', 1))
        db.session.commit()
        tasks = db.session.query(Task).all()
        for task in tasks:
            self.assertEqual(repr(task), '<Task Check email>')

    def test_users_cannot_see_task_modify_links_for_tasks_not_created_by_them(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.register('Ferdyshenko', 'ferd@ysh.com', 'ferdys', 'ferdys')
        self.login('Ferdyshenko', 'ferdys')
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertNotIn(b'Mark as complete', response.data)
        self.assertNotIn(b'Delete', response.data)

    def test_users_can_see_task_modify_links_for_tasks_created_by_them(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.register('Ferdyshenko', 'ferd@ysh.com', 'ferdys', 'ferdys')
        self.login('Ferdyshenko', 'ferdys')
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(b'complete/2/', response.data)
        self.assertIn(b'delete/2/', response.data)

    def test_admins_can_see_task_modify_links_for_all_tasks(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Norris', 'nor')
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(b'complete/1/', response.data)
        self.assertIn(b'delete/1/', response.data)
        self.assertIn(b'complete/2/', response.data)
        self.assertIn(b'delete/2/', response.data)


if __name__ == '__main__':
    unittest.main()
