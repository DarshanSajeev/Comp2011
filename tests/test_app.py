import unittest
import datetime
from app import app, db
from app.models import User, Post
from flask import url_for

class SocialMediaTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        # Create a test user
        self.user = User(username='testuser', password='password', age=datetime.date(2000, 1, 1), email='test@example.com')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, username, password):
        return self.app.post(url_for('login'), data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def test_addtaskroute(self):
        response = self.app.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_home_page(self):
        with self.app.session_transaction() as sess:
            sess['username'] = 'testuser'
        response = self.app.get(url_for('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Home', response.data)

    def test_register(self):
        response = self.app.post(url_for('register'), data=dict(
            username='newuser',
            password='newpassword',
            age='1990-01-01',
            email='newuser@example.com'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful!', response.data)

    def test_login(self):
        response = self.login('testuser', 'password')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successful!', response.data)

    def test_create_post(self):
        with self.app.session_transaction() as sess:
            sess['username'] = 'testuser'
        response = self.app.post(url_for('create_post'), data=dict(
            content='Test post content'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Post created successfully!', response.data)

    def test_follow_user(self):
        with self.app.session_transaction() as sess:
            sess['username'] = 'testuser'
        response = self.app.post(url_for('follow', username='newuser'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You are now following newuser!', response.data)

    def test_like_post(self):
        with self.app.session_transaction() as sess:
            sess['username'] = 'testuser'
        # Create a post to like
        post = Post(content='Test post', author=self.user)
        db.session.add(post)
        db.session.commit()

        response = self.app.post(url_for('like_post', post_id=post.id), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Post liked!', response.data)

if __name__ == '__main__':
    unittest.main()
