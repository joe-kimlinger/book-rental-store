
import os
import tempfile
import pytest
from argon2 import PasswordHasher
import datetime
import base64


from book_rental_store_api import create_app
from book_rental_store_api.db import init_db, get_db




class TestHelper():


    def __init__(self, app):
        self.app = app


    def create_book(self, title='Test Title', author='Test Author', rental_due_date='', days_rented=0, renting_user_id=None, book_type_id=1):
        with self.app.app_context():
            db = get_db()
            db.execute('INSERT INTO books_book (title, author, rental_due_date, days_rented, renting_user_id, book_type_id) VALUES (?,?,?,?,?,?)',
                [title, author, rental_due_date, days_rented, renting_user_id, book_type_id])
            db.commit()
    
    def create_user(self, username, password):
        self.username = username
        self.password = password
        with self.app.app_context():
            db = get_db()
            ph = PasswordHasher()
            pw = "argon2" + ph.hash(password)
            db.execute('INSERT INTO auth_user (password, is_superuser, username, last_name, email, is_staff, is_active, date_joined, first_name) VALUES (?,?,?,?,?,?,?,?,?)',
                [pw, False, username, 'last_name', 'email@email.com', False, True, datetime.datetime.now(), 'first_name'])
            db.commit()
    
    def get_auth_header(self):
        base64_string = base64.b64encode(f"{self.username}:{self.password}".encode('utf-8')).decode('utf-8')
        return f"Basic {base64_string}"


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    # create the app with common test config
    app = create_app({"TESTING": True, "DATABASE": db_path})

    # create the database and load test data
    with app.app_context():
        init_db()
        #get_db().executescript(_data_sql)

    yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def test_db(app):
    return TestHelper(app)