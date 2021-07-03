# Book Rental Store Web Application


## Setup

1. Install [venv](https://docs.python.org/3/library/venv.html) and create a new virtual environment called env
2. Activate the virtual environment

     `source bin/activate/env`

3. Install requirements

    `pip install -r requirements.txt`

4. Run the development server

    `python manage.py runserver`

5. Navigate to http://localhost:8000 to see the application running


## Running

Run development server

`python manage.py runserver`



## Testing

Test the books application 

`python manage.py test books`


Develop coverage report for unit tests

`coverage run --source='.' manage.py test books`

See test coverage

`coverage report` 

or 

`coverage html`

**Coverage report is in test_coverage_reports folder under report.txt**


# Book Rental Store API

## Authentication
Send a username and password using basic authentication.  The `Authentication` header should be in the format `Bearer <credential_string>` where <credential_string> is a base64-encoded string in the format username:password

## Routes
The API consists of the following routes:


### Books `/api/v1/resources/books`

**Allowed methods**: GET

**Details**: filter on book title and author using query params

**Response**:
```
{ "books": <list_of_book_objects>}
```
**Example**:
GET /api/v1/resources/books?author=MyAuthor

returns 
```
{
    "books": [
        {
            "id": 1,
            "title": "A Book Title",
            "author": "MyAuthor",
            "status": "Available",
            "type": "Regular",
            "rental_minimum_charge": 2.00,
            "rental_minimum_days": 2,
            "regular_rental_charge": 1.50
        },
        {
            "id": 2
            "title": "A Different Book Title",
            "author": "MyAuthor",
            "status": "Rented",
            "type": "Fiction",
            "available_date": "07/06/2021",
            "rental_minimum_charge": 0.00,
            "rental_minimum_days": 0,
            "regular_rental_charge": 1.50
        }   
    ]
}
```

### Single Book `/api/v1/resources/book/<int:book_id>`

**Allowed methods**: GET, PUT

**Details**: GET to retrieve a book and PUT to rent an un-rented book

**Response**: Response is a book object with id, title, author, status, book type, and rental rates (and due date if currently renting)
```
{
    "id": 2
    "title": "A Book Title",
    "author": "MyAuthor",
    "status": "Rented",
    "type": "Novel",
    "available_date": "07/06/2021",
    "rental_minimum_charge": 4.50,
    "rental_minimum_days": 3,
    "regular_rental_charge": 1.50
}
```
**Example**:
PUT /api/v1/resources/books/1
```
{
    "days_to_rent": 10
}
```
returns 
```
{
    "id": 1
    "title": "A Book Title",
    "author": "MyAuthor",
    "status": "Rented",
    "type": "Novel",
    "due_date": "07/06/2021",
    "rental_minimum_charge": 4.50,
    "rental_minimum_days": 3,
    "regular_rental_charge": 1.50,
    "total_rental_charge": 15.00
}
```

### My Books `/api/v1/resources/books/mybooks`

**Allowed methods**: GET

**Details**: filter my currently rented books title and author using query params

**Response**:
```
{ "books": <list_of_book_objects>}
```
**Example**:
GET /api/v1/resources/books/mybooks?author=MyAuthor

returns 
```
{
    "books": [
        {
            "title": "A Book Title",
            "author": "MyAuthor",
            "status": "Rented",
            "type": "Novel",
            "due_date": "07/22/2021",
            "rental_minimum_charge": 4.50,
            "rental_minimum_days": 3,
            "regular_rental_charge": 1.50,
            "total_rental_charge": 15.00
        },
        {
            "title": "A Different Book Title",
            "author": "MyAuthor",
            "status": "Rented",
            "type": "Fiction",
            "due_date": "07/06/2021",
            "rental_minimum_charge": 0.00,
            "rental_minimum_days": 0,
            "regular_rental_charge": 3.00,
            "total_rental_charge": 6.00
        }   
    ]
}
```

