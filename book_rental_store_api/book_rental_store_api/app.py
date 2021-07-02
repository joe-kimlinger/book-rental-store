from flask import Flask
from flask import request
from flask import jsonify
from decouple import config
from flask import session
from db import query_db, close_connection
from auth import login


app = Flask(__name__)
app.secret_key = config('SECRET_KEY')


@app.route("/api/v1/resources/books/all", methods=['GET'])
def index():
    book_list = query_db("select * from books_book")
    return {'books': book_list}


@app.route("/api/v1/resources/books/<int:book_id>", methods=['GET', 'POST'])
def show_book(book_id):
    login_err = login()
    
    if request.method == 'GET':
        return f"This is book {book_id}"
    else:
        if login_err:
            return jsonify(login_err), 401
        else:
            return f"Renting book {book_id}"


@app.route("/api/v1/resources/books/mybooks", methods=['GET'])
def my_books(book_id):
    return f"This is book {book_id}"


@app.teardown_appcontext
def teardown(exception):
    close_connection(exception)