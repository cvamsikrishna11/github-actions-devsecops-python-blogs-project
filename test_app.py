import unittest
from app import app, db
from models import User, Post

class BasicTests(unittest.TestCase):
    def setUp(self):
        # Set up the app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        
        # Set up the database
        with app.app_context():
            db.create_all()

    def tearDown(self):
        # Tear down any data after tests are done
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_main_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Blog!', response.data)

    def test_login_logout(self):
        # Create a user
        with app.app_context():
            user = User(username="testuser", password="testpassword")
            db.session.add(user)
            db.session.commit()

        # Login
        response = self.app.post('/login', data=dict(username="testuser", password="testpassword"), follow_redirects=True)
        self.assertIn(b'Logged in successfully', response.data)

        # Logout
        response = self.app.get('/logout', follow_redirects=True)
        self.assertIn(b'Logged out', response.data)

    def test_create_post(self):
        # Log in user
        with app.app_context():
            user = User(username="testposter", password="password123")
            db.session.add(user)
            db.session.commit()
        self.app.post('/login', data=dict(username="testposter", password="password123"), follow_redirects=True)

        # Create post
        response = self.app.post('/create', data=dict(title="New Post", content="Content of new post"), follow_redirects=True)
        self.assertIn(b'Post created', response.data)

        # Check post exists
        with app.app_context():
            post = Post.query.filter_by(title="New Post").first()
            self.assertIsNotNone(post)
            self.assertEqual(post.content, "Content of new post")

# Run the tests
if __name__ == "__main__":
    unittest.main()
