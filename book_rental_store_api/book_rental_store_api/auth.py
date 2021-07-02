from book_rental_store_api.db import get_db
from flask import session
from flask import redirect
from flask import url_for
from flask import request
from argon2 import PasswordHasher
import base64



def login():
    auth_header = request.headers["Authorization"].replace("Basic", "").strip()
    auth_header = base64.b64decode(auth_header)
    auth_header = auth_header.decode('utf-8')

    username = auth_header.split(':')[0]
    password = auth_header.split(':')[1]
    db = get_db()
    error = None
    user = db.execute(
        "SELECT * FROM auth_user WHERE username = ?", (username,)
    ).fetchone()

    if user is None:
        error = {'error': f"Incorrect username.  To sign up, visit {request.url_root}/accounts/signup"}
    else:
        pwd =  user["password"].replace("argon2", "", 1)
        ph = PasswordHasher()
        if not ph.verify(pwd, password):
            error = {'error': "Incorrect password."}
        else:
            return user

    return error