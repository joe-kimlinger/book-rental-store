import datetime

def test_book_get_empty_table(client):
    rv = client.get('/api/v1/resources/books/1')
    assert rv.status_code == 404
    assert rv.get_json() == "No book found with id 1"


def test_book_get_available_null_user(client, test_helper):
    test_helper.create_book(rental_due_date=datetime.datetime.now() + datetime.timedelta(days=3))
    rv = client.get('/api/v1/resources/books/1')
    assert rv.status_code == 200
    res = rv.get_json()
    assert len(res) == 8
    assert res.get('id') == 1
    assert res.get('title') == 'Test Title'
    assert res.get('author') == 'Test Author'
    assert res.get('status') == 'Available'
    assert res.get('type') == 'Regular'
    assert res.get('rental_minimum_charge') == 2.00
    assert res.get('rental_minimum_days') == 2
    assert res.get('regular_rental_charge') == 1.50


def test_book_get_available_past_due(client, test_helper):
    test_helper.create_book(renting_user_id=2, rental_due_date=datetime.datetime.now() + datetime.timedelta(days=-3))
    rv = client.get('/api/v1/resources/books/1')
    assert rv.status_code == 200
    res = rv.get_json()
    assert len(res) == 8
    assert res.get('id') == 1
    assert res.get('title') == 'Test Title'
    assert res.get('author') == 'Test Author'
    assert res.get('status') == 'Available'
    assert res.get('type') == 'Regular'
    assert res.get('rental_minimum_charge') == 2.00
    assert res.get('rental_minimum_days') == 2
    assert res.get('regular_rental_charge') == 1.50


def test_book_get_not_found(client, test_helper):
    test_helper.create_book()
    rv = client.get('/api/v1/resources/books/2')
    assert rv.status_code == 404
    res = rv.get_json()
    assert res == "No book found with id 2"


def test_book_get_someone_else_renting(client, test_helper):
    due_date = datetime.datetime.now() + datetime.timedelta(days=3)
    test_helper.create_book(rental_due_date=due_date, 
                        renting_user_id=2, book_type_id=3)
    rv = client.get('/api/v1/resources/books/1')
    assert rv.status_code == 200
    res = rv.get_json()
    assert len(res) == 9
    assert res.get('id') == 1
    assert res.get('title') == 'Test Title'
    assert res.get('author') == 'Test Author'
    assert res.get('status') == 'Rented'
    assert res.get('type') == 'Fiction'
    assert res.get('available_date') == str(due_date)[:16]
    assert res.get('rental_minimum_charge') == 0.00
    assert res.get('rental_minimum_days') == 0
    assert res.get('regular_rental_charge') == 3.00


def test_book_get_me_renting(client, test_helper):
    due_date = datetime.datetime.now() + datetime.timedelta(days=3)
    test_helper.create_user('test_user', 'test_password')

    test_helper.create_book(rental_due_date=due_date, days_rented=3,
                        renting_user_id=1, book_type_id=3)
    rv = client.get('/api/v1/resources/books/1', headers={"Authorization": test_helper.get_auth_header()})
    assert rv.status_code == 200
    res = rv.get_json()
    assert len(res) == 10
    assert res.get('id') == 1
    assert res.get('title') == 'Test Title'
    assert res.get('author') == 'Test Author'
    assert res.get('status') == 'Rented'
    assert res.get('type') == 'Fiction'
    assert res.get('due_date') == str(due_date)[:16]
    assert res.get('rental_minimum_charge') == 0.00
    assert res.get('rental_minimum_days') == 0
    assert res.get('regular_rental_charge') == 3.00
    assert res.get('total_rental_charge') == 9.00


def test_book_put_not_logged_in(client):
    rv = client.put('/api/v1/resources/books/1')
    assert rv.status_code == 401
    res = rv.get_json()
    assert res == "Unauthorized"


def test_book_put_available(client, test_helper):
    due_date = datetime.datetime.now() + datetime.timedelta(days=3)
    test_helper.create_user('test_user', 'test_password')

    test_helper.create_book(book_type_id=3)

    rv = client.put('/api/v1/resources/books/1', 
                    headers={"Authorization": test_helper.get_auth_header()},
                    data={'days_to_rent': 3})
    assert rv.status_code == 201    
    res = rv.get_json()
    assert len(res) == 10
    assert res.get('id') == 1
    assert res.get('title') == 'Test Title'
    assert res.get('author') == 'Test Author'
    assert res.get('status') == 'Rented'
    assert res.get('type') == 'Fiction'
    assert res.get('due_date') == str(due_date)[:16]
    assert res.get('rental_minimum_charge') == 0.00
    assert res.get('rental_minimum_days') == 0
    assert res.get('regular_rental_charge') == 3.00
    assert res.get('total_rental_charge') == 9.00


def test_book_put_already_rented_another_user(client, test_helper):
    due_date = datetime.datetime.now() + datetime.timedelta(days=3)
    test_helper.create_user('test_user', 'test_password')

    test_helper.create_book(book_type_id=3, rental_due_date=due_date, renting_user_id=3)

    rv = client.put('/api/v1/resources/books/1', 
                    headers={"Authorization": test_helper.get_auth_header()},
                    data={'days_to_rent': 3})
    assert rv.status_code == 403 
    res = rv.get_json()
    assert res == "Sorry, someone else is renting this right now."


def test_book_put_already_rented_by_me(client, test_helper):
    due_date = datetime.datetime.now() + datetime.timedelta(days=3)
    test_helper.create_user('test_user', 'test_password')

    test_helper.create_book(book_type_id=3, rental_due_date=due_date, renting_user_id=1)

    rv = client.put('/api/v1/resources/books/1', 
                    headers={"Authorization": test_helper.get_auth_header()},
                    data={'days_to_rent': 3})
    assert rv.status_code == 403 
    res = rv.get_json()
    assert res == "You're already renting this book."


def test_book_put_too_many_days(client, test_helper):
    test_helper.create_user('test_user', 'test_password')

    test_helper.create_book(book_type_id=3)

    rv = client.put('/api/v1/resources/books/1', 
                    headers={"Authorization": test_helper.get_auth_header()},
                    data={'days_to_rent': 60})
    assert rv.status_code == 400
    res = rv.get_json()
    assert res == "Please provide a days_to_rent between 1 and 30 days"


def test_book_put_negative_days(client, test_helper):
    test_helper.create_user('test_user', 'test_password')

    test_helper.create_book(book_type_id=3)

    rv = client.put('/api/v1/resources/books/1', 
                    headers={"Authorization": test_helper.get_auth_header()},
                    data={'days_to_rent': -3})
    assert rv.status_code == 400
    res = rv.get_json()
    assert res == "Please provide a days_to_rent between 1 and 30 days"


def test_book_put_non_int_input(client, test_helper):
    test_helper.create_user('test_user', 'test_password')

    test_helper.create_book(book_type_id=3)

    rv = client.put('/api/v1/resources/books/1', 
                    headers={"Authorization": test_helper.get_auth_header()},
                    data={'days_to_rent': "non-int"})
    assert rv.status_code == 400
    res = rv.get_json()
    assert res == "Please provide a days_to_rent between 1 and 30 days"


def test_book_put_no_days(client, test_helper):
    due_date = datetime.datetime.now() + datetime.timedelta(days=3)
    test_helper.create_user('test_user', 'test_password')

    test_helper.create_book(book_type_id=3, rental_due_date=due_date, renting_user_id=1)

    rv = client.put('/api/v1/resources/books/1', 
                    headers={"Authorization": test_helper.get_auth_header()},
                    data={})
    assert rv.status_code == 400
    res = rv.get_json()
    assert res == "Please provide days_to_rent in the request body."


def test_book_put_no_body(client, test_helper):
    due_date = datetime.datetime.now() + datetime.timedelta(days=3)
    test_helper.create_user('test_user', 'test_password')

    test_helper.create_book(book_type_id=3, rental_due_date=due_date, renting_user_id=1)

    rv = client.put('/api/v1/resources/books/1', 
                    headers={"Authorization": test_helper.get_auth_header()})
    assert rv.status_code == 400
    res = rv.get_json()
    assert res == "Please provide days_to_rent in the request body."