import datetime
from flask import Blueprint
from flask import request
from flask import jsonify
from book_rental_store_api.db import query_db
from book_rental_store_api.auth import login
import re


bp = Blueprint("books", __name__)

BASE_QUERY = "SELECT book.id, book.title, book.author, book.rental_due_date, book.renting_user_id, book.days_rented, \
              book_type.book_type, book_type.min_days_rate, book_type.min_days, book_type.rental_rate \
              FROM books_book book \
              JOIN books_booktype book_type ON book.book_type_id = book_type.id"

@bp.route("/api/v1/resources/books", methods=['GET'])
def index():
    query = BASE_QUERY
    query_filter_text = []
    query_fields = []
    book_list = []

    user = login()

    if request.args.get('title'):
        query_filter_text.append('title=?')
        query_fields.append(request.args.get('title'))
    if request.args.get('author'):
        query_filter_text.append('author=?')
        query_fields.append(request.args.get('author'))

    if len(query_fields):
        query += ' WHERE ' + ' AND '.join(query_filter_text)

    book_list = [format_book(book, user.get('id')) for book in query_db(query, query_fields)]

    return {'books': book_list}


@bp.route("/api/v1/resources/books/<int:book_id>", methods=['GET', 'PUT'])
def show_book(book_id):
    query = f"{BASE_QUERY} WHERE book.id=?"
    
    user = login()
    if request.method == 'PUT' and 'error' in user:
        return jsonify(user['error']), 401
    
    books = query_db(query, [book_id])

    if not len(books):
        return jsonify(f'No book found with id {book_id}'), 404
    
    book = books[0]
    
    if request.method == 'GET':
        return format_book(books[0], user.get('id'))
    else:
        if 'days_to_rent' not in request.values:
            return jsonify("Please provide days_to_rent in the request body."), 400
        
        try:
            days_to_rent = int(request.values.get('days_to_rent'))
        except ValueError:
            return jsonify("Please provide a days_to_rent between 1 and 30 days"), 400
            
        if type(days_to_rent) != int or days_to_rent < 1 or days_to_rent >= 30:
            return jsonify("Please provide a days_to_rent between 1 and 30 days"), 400

        if not is_available(book):
            if book['renting_user_id'] == user['id']:
                return jsonify("You're already renting this book."), 403
            else:
                return jsonify("Sorry, someone else is renting this right now."), 403

        due_date = datetime.datetime.now() + datetime.timedelta(days=days_to_rent)
        update_query = "UPDATE books_book SET rental_due_date=?, renting_user_id=?, days_rented=? WHERE id=?"
        query_db(update_query, [due_date, user['id'], days_to_rent, books[0]['id']])

        books = query_db(f"{BASE_QUERY} WHERE book.id=?", [book['id']])
        return format_book(books[0], user['id']), 201


@bp.route("/api/v1/resources/books/mybooks", methods=['GET'])
def my_books():
    query = f"{BASE_QUERY} WHERE book.renting_user_id=?"
    query_filter_text = []
    query_fields = []
    book_list = []

    user = login()
    if 'error' in user:
        return jsonify(user['error']), 401

    query_fields.append(user.get('id'))

    if request.args.get('title'):
        query_filter_text.append('title=?')
        query_fields.append(request.args.get('title'))
    if request.args.get('author'):
        query_filter_text.append('author=?')
        query_fields.append(request.args.get('author'))

    if len(query_fields) > 1:
        query += ' AND ' + ' AND '.join(query_filter_text)

    book_list = [format_book(book, user.get('id')) 
                 for book in query_db(query, query_fields)
                 if not is_available(book)]

    return {'my_books': book_list}


def format_book(book, user_id=None):
    new_book = {}
    new_book['id'] = book['id'] 
    new_book['title'] = book['title'] 
    new_book['author'] = book['author']
    new_book['type'] = book['book_type']
    new_book['rental_minimum_charge'] = book['min_days_rate'] * book['min_days']
    new_book['rental_minimum_days'] = book['min_days']
    new_book['regular_rental_charge'] = book['rental_rate']
    
    book['rental_due_date'] = re.sub(':[^\.:]*\..*$', '', book['rental_due_date'])
    if is_available(book):
        new_book['status'] = 'Available'
    else:
        new_book['status'] = 'Rented'
        if user_id and user_id == book['renting_user_id']:
            new_book['due_date'] = book['rental_due_date']
            new_book['total_rental_charge'] = rental_charge(book)
        else:
            new_book['available_date'] = book['rental_due_date']
    
    print(new_book)

    return new_book


def is_available(book):
    return book['renting_user_id'] is None or book['rental_due_date'] < re.sub(':[^\.:]*\..*$', '', str(datetime.datetime.now()))


def rental_charge(book):
    rental_charge = book['min_days'] * book['min_days_rate'] + \
        book['rental_rate'] * max(0, book['days_rented'] - book['min_days'])
    return max(rental_charge, 0)