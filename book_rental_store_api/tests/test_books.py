import os
import tempfile
from flask import g


import pytest

from book_rental_store_api import create_app
from book_rental_store_api.db import init_db


def create_book(title='Test Title', author='Test Author', rental_due_date='', days_rented=0, renting_user_id=0, book_type_id=0):
    g.db.execute('INSERT INTO books_book (title, author, rental_due_date, days_rented, renting_user_id, book_type_id) VALUES (?,?,?,?,?,?)',
        title, author, rental_due_date, days_rented, renting_user_id, book_type_id)
    g.db.commit()

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({'TESTING': True, 'DATABASE': db_path})

    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

    os.close(db_fd)
    os.unlink(db_path)


def test_book_list_empty_table(client):
    rv = client.get('/api/v1/resources/books/all')
    res = rv.get_json()
    assert 'books' in res.keys()
    assert res['books'] == []



def test_book_list_books(client):
    create_book()
    rv = client.get('/api/v1/resources/books/all')
    res = rv.get_json()
    assert 'books' in res.keys()
    assert res['books'][0]['title'] == 'Test Title'