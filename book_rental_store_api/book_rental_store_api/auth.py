from db import get_db
from flask import session
from flask import redirect
from flask import url_for
from flask import request
from argon2 import PasswordHasher



def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM auth_user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        else:
            pwd =  user["password"].replace("argon2", "", 1)
            ph = PasswordHasher()
            print(pwd)
            if not ph.verify(pwd, password):
                error = "Incorrect password."

    return error