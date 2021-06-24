# Book Rental Store


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

Run production server

TODO


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

