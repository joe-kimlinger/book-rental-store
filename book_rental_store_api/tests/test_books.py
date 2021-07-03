import datetime


def test_book_list_empty_table(client):
    rv = client.get('/api/v1/resources/books')
    res = rv.get_json()
    assert 'books' in res
    assert res['books'] == []


def test_book_list_books(client, test_db):
    due_date = datetime.datetime.now() + datetime.timedelta(days=3)
    test_db.create_book(rental_due_date=due_date, renting_user_id=1)
    test_db.create_book(title='Book 2', author='Author 2', book_type_id=2)
    rv = client.get('/api/v1/resources/books')
    res = rv.get_json()
    assert 'books' in res
    assert res['books'][0].get('title') == 'Test Title'
    assert res['books'][0].get('author') == 'Test Author'
    assert res['books'][0].get('status') == 'Rented'
    assert res['books'][0].get('type') == 'Regular'
    assert res['books'][0].get('available_date') == str(due_date)[:16]
    assert res['books'][0].get('rental_minimum_charge') == 2.00
    assert res['books'][0].get('rental_minimum_days') == 2
    assert res['books'][0].get('regular_rental_charge') == 1.50
    assert res['books'][1].get('title') == 'Book 2'
    assert res['books'][1].get('author') == 'Author 2'
    assert res['books'][1].get('author') == 'Author 2'
    assert res['books'][1].get('status') == 'Available'
    assert res['books'][1].get('type') == 'Novel'
    assert 'total_rental_charge' not in res['books'][0]
    assert 'total_rental_charge' not in res['books'][1]


def test_book_list_title_filter(client, test_db):
    test_db.create_book(title='TestTitle')
    test_db.create_book(title='Book 2', author='Author 2')
    rv = client.get('/api/v1/resources/books?title=TestTitle')
    res = rv.get_json()
    assert 'books' in res
    assert len(res['books']) == 1
    assert res['books'][0].get('title') == 'TestTitle'
    assert res['books'][0].get('author') == 'Test Author'


def test_book_list_author_filter(client, test_db):
    test_db.create_book(author='TestAuthor')
    test_db.create_book(author='TestAuthor')
    test_db.create_book(author='Not returned')
    rv = client.get('/api/v1/resources/books?author=TestAuthor')
    res = rv.get_json()
    assert 'books' in res
    assert len(res['books']) == 2
    assert res['books'][0].get('author') == 'TestAuthor'
    assert res['books'][1].get('author') == 'TestAuthor'


def test_book_list_title_and_author_filter(client, test_db):
    test_db.create_book(title='Not returned', author='TestAuthor')
    test_db.create_book(title='TestTitle', author='TestAuthor')
    test_db.create_book(title='TestTitle', author='Not returned')
    rv = client.get('/api/v1/resources/books?title=TestTitle&author=TestAuthor')
    res = rv.get_json()
    assert 'books' in res
    assert len(res['books']) == 1
    assert res['books'][0].get('title') == 'TestTitle'
    assert res['books'][0].get('author') == 'TestAuthor'