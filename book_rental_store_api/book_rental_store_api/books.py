from flask import Blueprint
from flask import request
from flask import jsonify
from flask.globals import current_app
from book_rental_store_api.db import query_db
from book_rental_store_api.auth import login


bp = Blueprint("books", __name__)


@bp.route("/api/v1/resources/books/all", methods=['GET'])
def index():
    book_list = query_db("select * from books_book")
    return {'books': book_list}


@bp.route("/api/v1/resources/books/<int:book_id>", methods=['GET', 'POST'])
def show_book(book_id):
    login_err = login()
    
    if request.method == 'GET':
        return f"This is book {book_id}"
    else:
        if login_err:
            return jsonify(login_err), 401
        else:
            return f"Renting book {book_id}"


@bp.route("/api/v1/resources/books/mybooks", methods=['GET'])
def my_books(book_id):
    return f"This is book {book_id}"