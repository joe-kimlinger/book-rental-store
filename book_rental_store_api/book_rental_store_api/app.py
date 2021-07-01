from flask import Flask
from flask import request
from flask import jsonify
from decouple import config
from flask import session
from db import query_db, close_connection


app = Flask(__name__)
app.secret_key = config('SECRET_KEY')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route("/books", methods=['GET'])
def index():
    book_list = query_db("select * from books_book")
    return {'books': book_list}


@app.route("/books/<int:book_id>", methods=['GET', 'POST'])
def show_book(book_id):
    if request.method == 'GET':
        return f"This is book {book_id}"
    else:
        return f"Renting book {book_id}"


@app.route("/books/mybooks", methods=['GET'])
def my_books(book_id):
    return f"This is book {book_id}"


@app.teardown_appcontext
def teardown(exception):
    close_connection(exception)