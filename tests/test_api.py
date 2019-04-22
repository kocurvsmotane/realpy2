import json
import os
import unittest
from datetime import date

from project import app, db
from project._config import basedir
from project.models import Task


TEST_DB = 'test.db'


class APITests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################

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

    ########################
    #### helper methods ####
    ########################

    def add_tasks(self):
        db.session.add(
            Task(
                "Run around in circles",
                date(2015, 10, 22),
                10,
                date(2015, 10, 5),
                1,
                1
            )
        )
        db.session.commit()

        db.session.add(
            Task(
                "Purchase Real Python",
                date(2016, 2, 23),
                10,
                date(2016, 2, 7),
                1,
                1
            )
        )
        db.session.commit()

    # helper functions

    def login(self, name, password):
        return self.app.post('/', data=dict(name=name, password=password), follow_redirects=True)

    def register(self, name, email, password, confirm):
        return self.app.post('register/', data=dict(name=name, email=email, password=password, confirm=confirm), follow_redirects=True)

    ###############
    #### tests ####
    ###############

    def test_collection_endpoint_returns_correct_data(self):
        self.add_tasks()
        response = self.app.get('api/v1/tasks/', follow_redirects=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.mimetype, 'application/json')
        self.assertIn(b'Run around in circles', response.data)
        self.assertIn(b'Purchase Real Python', response.data)

    def test_resource_endpoint_returns_correct_data(self):
        self.add_tasks()
        response = self.app.get('api/v1/tasks/2/', follow_redirects=True)
        self.assertEquals(200, response.status_code)
        self.assertEquals('application/json', response.mimetype)
        self.assertIn(b'Purchase Real Python', response.data)
        self.assertNotIn(b'Run around in circles', response.data)

    def test_invalid_resource_endpoint_returns_error(self):
        self.add_tasks()
        response = self.app.get('api/v1/tasks/209/', follow_redirects=True)
        self.assertEquals(404, response.status_code)
        self.assertEquals('application/json', response.mimetype)
        self.assertIn(b'Element does not exist', response.data)

    def test_post_new_task(self):
        task = {
            'name': "Task for successful adding", 'due_date': date(2019, 5, 1), 'priority': 1, 'status': 1
        }
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        response = self.app.post('api/v2/tasks/', follow_redirects=True, data=task)
        self.assertEqual(200, response.status_code)
        response = self.app.get('api/v2/tasks/', follow_redirects=True)
        resp_data = json.loads(response.data)[0]
        self.assertIn("Task for successful adding", resp_data['task_name'])

    def test_post_unauthorized(self):
        task = {
            'name': "Task for test", 'due_date': date(2019, 5, 1), 'priority': 1, 'status': 1
        }
        response = self.app.post('api/v2/tasks/', follow_redirects=True, data=task)
        self.assertEqual(401, response.status_code)
        response = self.app.get('api/v2/tasks/', follow_redirects=True)
        self.assertEqual(0, len(json.loads(response.data)))


if __name__ == "__main__":
    unittest.main()
