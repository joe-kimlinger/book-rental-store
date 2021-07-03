from book_rental_store_api.db import get_db
from flask import request
from argon2 import PasswordHasher
import base64
import re



def login():
    if "Authorization" not in request.headers:
        return {"error": "Unauthorized"}
    auth_header = request.headers["Authorization"].replace("Basic", "").strip()
    auth_header = base64.b64decode(auth_header)
    auth_header = auth_header.decode('utf-8')


    username = auth_header.split(':')[0]
    password = auth_header.split(':')[1]
    db = get_db()

    user = db.execute(
        "SELECT * FROM auth_user WHERE username = ?", (username,)
    ).fetchone()

    if user is None:
        req_url = re.sub(":\d+", "", request.url_root)
        return {'error': f"Incorrect username.  To sign up, visit {req_url}accounts/signup"}
    else:
        pwd =  user["password"].replace("argon2", "", 1)
        ph = PasswordHasher()
        try:
            ph.verify(pwd, password)
        except:
            return {'error': "Incorrect password."}

    return user