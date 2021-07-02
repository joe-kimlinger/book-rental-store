import datetime

def test_book__get_empty_table(client):
    rv = client.get('/api/v1/resources/books/1')
    assert rv.status_code == 404


def test_book_get_one_entry(client, test_db):
    test_db.create_book()
    rv = client.get('/api/v1/resources/books/1')
    res = rv.get_json()
    assert len(res.keys()) == 4
    assert res['id'] == 1
    assert res['title'] == 'Test Title'
    assert res['author'] == 'Test Author'
    assert res['status'] == 'Available'
    assert res['type'] == 'Regular'
    assert False == True



def test_book_get_one_entry_wrong_id(client, test_db):
    test_db.create_book()
    rv = client.get('/api/v1/resources/books/2')
    res = rv.get_json()
    assert len(res.keys()) == 0


def test_book_get_someone_else_renting(client, test_db):
    test_db.create_book(rental_due_date=datetime.now + datetime.timedelta(days=3), renting_user_id=2)
    rv = client.get('/api/v1/resources/books/1')
    res = rv.get_json()
    assert len(res.keys()) == 4
    assert res['books'][0]['id'] == 1
    assert res['books'][0]['title'] == 'Test Title'
    assert res['books'][0]['author'] == 'Test Author'
    assert res['books'][0]['status'] == 'Available'