
import os
import tempfile
import pytest


from book_rental_store_api import create_app
from book_rental_store_api.db import init_db, get_db




class TestHelper():


    def __init__(self, app):
        self.app = app


    def create_book(self, title='Test Title', author='Test Author', rental_due_date='', days_rented=0, renting_user_id=0, book_type_id=1):
        with self.app.app_context():
            db = get_db()
            db.execute('INSERT INTO books_book (title, author, rental_due_date, days_rented, renting_user_id, book_type_id) VALUES (?,?,?,?,?,?)',
            [title, author, rental_due_date, days_rented, renting_user_id, book_type_id])
            db.commit()


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