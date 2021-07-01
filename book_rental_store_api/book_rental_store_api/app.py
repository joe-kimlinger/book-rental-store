from flask import Flask
from flask import request

app = Flask(__name__)

@app.route("/books", methods=['GET'])
def list_books():
    return "Here are my books: <books>"


@app.route("/books/<int:book_id>", methods=['GET', 'POST'])
def show_book(book_id):
    if request.method == 'GET':
        return f"This is book {book_id}"
    else:
        return f"Renting book {book_id}"


@app.route("/books/mybooks", methods=['GET'])
def my_books(book_id):
    return f"This is book {book_id}"