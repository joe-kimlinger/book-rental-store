import os

from flask import Flask
from decouple import config



def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_mapping(
            SECRET_KEY=config('SECRET_KEY'),
            # store the database in the instance folder
            DATABASE='../db.sqlite3',
        )
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register the database commands
    from book_rental_store_api import db

    db.init_app(app)

    # apply the blueprints to the app
    from book_rental_store_api import books

    app.register_blueprint(books.bp)

    return app