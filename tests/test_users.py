import os
import unittest

from project import app, db
from project._config import basedir
from project.models import User

TEST_DB = 'test.db'


class UsersTests(unittest.TestCase):

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

    def test_form_is_present_on_login_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please sign in to access your task list', response.data)

    def test_users_cannot_login_unless_registered(self):
        response = self.login('foo', 'bar')
        self.assertIn(b'Invalid username or password.', response.data)

    def test_users_can_login(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        response = self.login('Michael', 'python')
        self.assertIn(b'Welcome!', response.data)

    def test_invalid_form_data(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        response = self.login('alert("alert box!");', 'foo')
        self.assertIn(b'Invalid username or password.', response.data)

    def test_form_is_present_on_register_page(self):
        response = self.app.get('register/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please register to access the task list.', response.data)

    def test_user_registration(self):
        response = self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Thanks for registering. Please login.', response.data)

    def test_user_registration_error(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        response = self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.assertIn(b'That username and/or email already exist.', response.data)

    def test_logged_in_users_can_logout(self):
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        self.login('Michael', 'python')
        response = self.logout()
        self.assertIn(b'Goodbye!', response.data)

    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout()
        self.assertNotIn(b'Goodbye!', response.data)

    def test_user_login_field_errors(self):
        response = self.login('', 'python')
        self.assertIn(b'This field is required.', response.data)

    def test_string_representation_of_the_user_object(self):
        db.session.add(User('Pycat', 'pycat@pythonista.sk', 'pycat'))
        db.session.commit()
        users = db.session.query(User).all()
        for user in users:
            self.assertEqual(repr(user), '<User Pycat>')

    def test_default_user_role(self):
        db.session.add(User('Malkovich', 'malkovich@actor.com', 'malk'))
        db.session.commit()
        users = db.session.query(User).all()
        for user in users:
            self.assertEqual(user.role, 'user')

    def test_task_template_displays_logged_in_user_name(self):
        self.register('Ferdyshenko', 'ferd@ysh.com', 'ferdys', 'ferdys')
        self.login('Ferdyshenko', 'ferdys')
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn(b'Ferdyshenko', response.data)


if __name__ == '__main__':
    unittest.main()
