import datetime
from flask import Blueprint
from flask import request
from flask import jsonify
from flask.globals import session
from book_rental_store_api.db import query_db
from book_rental_store_api.auth import login
import re


bp = Blueprint("books", __name__)

BASE_QUERY = "SELECT * FROM books_book book JOIN books_booktype book_type ON book.book_type_id == book_type.id"

@bp.route("/api/v1/resources/books", methods=['GET'])
def index():
    query = BASE_QUERY
    query_filter_text = []
    query_fields = []
    book_list = []

    if request.args.get('title'):
        query_filter_text.append('title=?')
        query_fields.append(request.args.get('title'))
    if request.args.get('author'):
        query_filter_text.append('author=?')
        query_fields.append(request.args.get('author'))

    if len(query_fields):
        query += ' WHERE ' + ' AND '.join(query_filter_text)

    book_list = [format_book(book) for book in query_db(query, query_fields)]

    return {'books': book_list}


@bp.route("/api/v1/resources/books/<int:book_id>", methods=['GET', 'PUT'])
def show_book(book_id):
    login_err = login()
    
    if request.method == 'GET':
        query = f"{BASE_QUERY} WHERE book.id=?"
        books = query_db(query, [book_id])
        if len(books):
            return format_book(books[0])
        else:
            return jsonify(f'No book found with id {book_id}')
    else:
        if 'error' in login_err:
            return jsonify(login_err), 401
        else:
            return f"Renting book {book_id}"


@bp.route("/api/v1/resources/books/mybooks", methods=['GET'])
def my_books(book_id):
    return f"This is book {book_id}"


def format_book(book):
    new_book = {}
    new_book['title'] = book['title'] 
    new_book['author'] = book['author']
    new_book['type'] = book['book_type']
    new_book['rental_minimum_charge'] = book['min_days_rate'] * book['min_days']
    new_book['rental_minimum_days'] = book['min_days']
    new_book['regular_rental_charge'] = book['rental_rate']
    
    book['rental_due_date'] = re.sub(':[^\.:]*\..*$', '', book['rental_due_date'])
    if book['renting_user_id'] is None or book['rental_due_date'] < str(datetime.datetime.now()):
        new_book['status'] = 'Available'
    else:
        new_book['status'] = 'Rented'
        if session['user_id'] == book['renting_user_id']:
            new_book['due_date'] = book['rental_due_date']
        else:
            new_book['available_date'] = book['rental_due_date']
        

    return new_book