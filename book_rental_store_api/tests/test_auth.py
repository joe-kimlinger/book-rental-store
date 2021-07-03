def test_login_bad_username(client, test_helper):
    test_helper.username = "username"
    test_helper.password = "password"
    rv = client.get('/api/v1/resources/books/mybooks', 
                    headers={"Authorization": test_helper.get_auth_header()})
    assert rv.status_code == 401
    assert "Incorrect username." in rv.get_json()

def test_login_bad_password(client, test_helper):
    test_helper.create_user('test_user', 'test_password')

    test_helper.password = "password"
    rv = client.get('/api/v1/resources/books/mybooks', 
                    headers={"Authorization": test_helper.get_auth_header()})
    assert rv.status_code == 401
    assert rv.get_json() == "Incorrect password."
