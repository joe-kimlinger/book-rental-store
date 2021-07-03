import datetime


def test_my_books_empty_table(client, test_helper):
    test_helper.create_user('test_user', 'test_password')
    rv = client.get('/api/v1/resources/books/mybooks', 
                    headers={"Authorization": test_helper.get_auth_header()})
    res = rv.get_json()
    assert 'my_books' in res
    assert res['my_books'] == []


def test_my_books_not_logged_in(client):
    rv = client.get('/api/v1/resources/books/mybooks')
    assert rv.status_code == 401
    res = rv.get_json()
    assert res == "Unauthorized"


def test_my_books_books(client, test_helper):
    test_helper.create_user('test_user', 'test_password')

    due_date = datetime.datetime.now() + datetime.timedelta(days=3)
    test_helper.create_book(rental_due_date=due_date, days_rented=3, renting_user_id=1)
    test_helper.create_book(title='Book 2', author='Author 2', book_type_id=2)
    rv = client.get('/api/v1/resources/books/mybooks', 
                    headers={"Authorization": test_helper.get_auth_header()})
    res = rv.get_json()
    assert 'my_books' in res
    assert len(res['my_books']) == 1
    assert res['my_books'][0].get('title') == 'Test Title'
    assert res['my_books'][0].get('author') == 'Test Author'
    assert res['my_books'][0].get('status') == 'Rented'
    assert res['my_books'][0].get('type') == 'Regular'
    assert res['my_books'][0].get('due_date') == str(due_date)[:16]
    assert res['my_books'][0].get('rental_minimum_charge') == 2.00
    assert res['my_books'][0].get('rental_minimum_days') == 2
    assert res['my_books'][0].get('regular_rental_charge') == 1.50
    assert res['my_books'][0].get('total_rental_charge') == 3.50


def test_my_books_title_filter(client, test_helper):
    test_helper.create_user('test_user', 'test_password')

    due_date = datetime.datetime.now() + datetime.timedelta(days=3)
    test_helper.create_book(title='TestTitle', renting_user_id=1, rental_due_date=due_date)
    test_helper.create_book(title='TestTitle', renting_user_id=2, rental_due_date=due_date)
    test_helper.create_book(title='Book 2', author='Author 2', 
                        renting_user_id=1, rental_due_date=due_date)
    rv = client.get('/api/v1/resources/books/mybooks?title=TestTitle', 
                    headers={"Authorization": test_helper.get_auth_header()})
    res = rv.get_json()
    assert 'my_books' in res
    assert len(res['my_books']) == 1
    assert res['my_books'][0].get('title') == 'TestTitle'
    assert res['my_books'][0].get('author') == 'Test Author'


def test_my_books_author_filter(client, test_helper):
    test_helper.create_user('test_user', 'test_password')

    due_date = datetime.datetime.now() + datetime.timedelta(days=3)
    test_helper.create_book(title='Test title', author='TestAuthor', 
                        renting_user_id=1, rental_due_date=due_date)
    test_helper.create_book(title='Test title 2', author='TestAuthor', 
                        renting_user_id=1, rental_due_date=due_date)
    test_helper.create_book(author='Not returned', renting_user_id=1, rental_due_date=due_date)
    rv = client.get('/api/v1/resources/books/mybooks?author=TestAuthor', 
                    headers={"Authorization": test_helper.get_auth_header()})
    res = rv.get_json()
    assert 'my_books' in res
    assert len(res['my_books']) == 2
    assert res['my_books'][0].get('author') == 'TestAuthor'
    assert res['my_books'][1].get('author') == 'TestAuthor'


def test_my_books_title_and_author_filter(client, test_helper):
    test_helper.create_user('test_user', 'test_password')

    due_date = datetime.datetime.now() + datetime.timedelta(days=3)
    test_helper.create_book(title='Not returned', author='TestAuthor', 
                        renting_user_id=1, rental_due_date=due_date)
    test_helper.create_book(title='TestTitle', author='TestAuthor', 
                        renting_user_id=1, rental_due_date=due_date)
    test_helper.create_book(title='TestTitle', author='Not returned', 
                        renting_user_id=1, rental_due_date=due_date)
    rv = client.get('/api/v1/resources/books/mybooks?title=TestTitle&author=TestAuthor', 
                    headers={"Authorization": test_helper.get_auth_header()})
    res = rv.get_json()
    assert 'my_books' in res
    assert len(res['my_books']) == 1
    assert res['my_books'][0].get('title') == 'TestTitle'
    assert res['my_books'][0].get('author') == 'TestAuthor'