from django.http.response import HttpResponseRedirect
from django.test import TestCase, client
from django.contrib.auth.models import User
from django.urls.base import reverse
from django.utils import timezone
import datetime

from .models import Book


####### MODEL UNIT TESTS ##########

class BookModelTests(TestCase):

    def test_days_remaining_with_past_due_date(self):
        """
        days_remaining() should return 0 if the due_date is in the past
        """
        time = timezone.now() + datetime.timedelta(days=-3)
        past_due_book = Book(rental_due_date=time)
        self.assertEqual(past_due_book.days_remaining(), 0)
    

    def test_days_remaining_on_due_date(self):
        """
        days_remaining() should return 0 if the due_date less that 24 hours 
        from the current date
        """
        time = timezone.now() + datetime.timedelta(hours=12)
        almost_due_book = Book(rental_due_date=time)
        self.assertEqual(almost_due_book.days_remaining(), 0)


    def test_days_remaining_before_due_date(self):
        """
        check that days_remaining() lines up with configured delta
        """
        delta = 12
        time = timezone.now() + datetime.timedelta(days=delta, minutes=1)
        almost_due_book = Book(rental_due_date=time)
        self.assertEqual(almost_due_book.days_remaining(), delta)
    

    def test_rental_charge_empty_days_rented(self):
        """
        check that rental_charge() with emtpy days_rented raises exception
        """
        book = Book()
        with self.assertRaises(Exception) as exc:
            book.rental_charge()

        self.assertEqual(str(exc.exception), 'Error: days_rented is undefined')

            
    def test_rental_charge_past_due_date(self):
        """
        check that rental_charge() still gives total rental charge after due date
        """
        time = timezone.now() + datetime.timedelta(days=-6)
        past_due_book = Book(rental_due_date=time, days_rented=10)
        self.assertEqual(past_due_book.rental_charge(), 10.00)


    def test_rental_charge_before_due_date(self):
        """
        check that rental_charge() still gives total rental charge before due date
        """
        time = timezone.now() + datetime.timedelta(days=-6)
        almost_due_book = Book(rental_due_date=time, days_rented=10)
        self.assertEqual(almost_due_book.rental_charge(), 10.00)
    

    def test_rental_charge_different_rental_rate(self):
        """
        check that rental_charge() still gives total rental charge before due date
        """
        days_rented = 10
        rental_rate = 3.50
        book = Book(rental_rate=rental_rate, days_rented=days_rented)
        self.assertEqual(book.rental_charge(), rental_rate * days_rented)

    
    def test_past_due_past_due_date(self):
        """
        check that past_due() returns true for book past due date
        """
        time = timezone.now() + datetime.timedelta(days=-3)
        past_due_book = Book(rental_due_date=time)
        self.assertTrue(past_due_book.past_due())
    

    def test_past_due_before_due_date(self):
        """
        check that past_due() returns false for book before due date
        """
        time = timezone.now() + datetime.timedelta(days=5)
        almsot_due_book = Book(rental_due_date=time)
        self.assertFalse(almsot_due_book.past_due())


    def test_past_due_just_past_due_date(self):
        """
        check that past_due() returns true for book immediately after due date
        """
        time = timezone.now() + datetime.timedelta(seconds=-1)
        past_due_book = Book(rental_due_date=time)
        self.assertTrue(past_due_book.past_due())


    def test_str_conversion(self):
        """
        check that __str__() returns book title
        """
        title = 'My Title'
        book = Book(title=title)
        self.assertEqual(str(book), title)
    

    def test_str_conversion_no_title(self):
        """
        check that __str__() for book with no title returns empty string
        """
        book = Book()
        self.assertEqual(str(book), '')

####### VIEW UNIT TESTS ##########

class BooksViewTests(TestCase):

    def test_books_view_no_books(self):
        """
        If no books are available display appropriate message
        """
        response = self.client.get(reverse('books'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are currently no books available.")
        self.assertQuerysetEqual(response.context['books_list'], [])


    def test_books_view_no_books_available(self):
        """
        If all books are rented, display no available message
        """
        time = timezone.now() + datetime.timedelta(days=3)
        rented_book = Book.objects.create(title='Test Book', rental_due_date=time, renting_user=User.objects.create())
        response = self.client.get(reverse('books'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are currently no books available.")
        self.assertQuerysetEqual(response.context['books_list'], [])
    

    def test_books_view_books_available(self):
        """
        Display books that are available
        """
        time = timezone.now() + datetime.timedelta(days=-3)
        available_book = Book.objects.create(title='Test Book', rental_due_date=time)
        response = self.client.get(reverse('books'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['books_list'],
            [available_book],
        )
    

    def test_books_view_some_books_rented(self):
        """
        Display books that are available but not rented ones
        Books are available if they're past due OR their renting_user is null
        """
        new_user = User.objects.create()
        time_1 = timezone.now() + datetime.timedelta(days=3)
        rented_book = Book.objects.create(title='Test Book', rental_due_date=time_1, renting_user=new_user)
        available_book_1 = Book.objects.create(title='Test Book', rental_due_date=time_1)
        time_2 = timezone.now() + datetime.timedelta(days=-3)
        available_book_2 = Book.objects.create(title='Test Book', rental_due_date=time_2, renting_user=new_user)
        response = self.client.get(reverse('books'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['books_list'],
            [available_book_1, available_book_2],
            ordered=False
        )
    

    def test_books_view_multiple_books_available(self):
        """
        If multiple books are available, display books them all
        """
        time_1 = timezone.now() + datetime.timedelta(days=-3)
        available_book_1 = Book.objects.create(title='Test Book 1', rental_due_date=time_1)
        time_2 = timezone.now() + datetime.timedelta(days=-5)
        available_book_2 = Book.objects.create(title='Test Book 2', rental_due_date=time_2)
        response = self.client.get(reverse('books'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['books_list'],
            [available_book_1, available_book_2],
            ordered=False
        )


class MyBooksViewTests(TestCase):
    test_username = 'unit-test-user'
    test_email = 'unit@test.com'
    test_password = 'unittest'

    def setUp(self):
        self.user = User.objects.create_user(self.test_username, self.test_email, self.test_password)


    def test_mybooks_not_logged_in_redirect(self):
        """
        If not logged in, navigating to my_books should redirect with mybooks as return
        """
        response = self.client.get(reverse('my_books'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/accounts/login/?next=/books/mybooks')


    def test_mybooks_view_no_rented_books(self):
        """
        If no books are rented display appropriate message
        """
        self.client.login(username=self.test_username, password=self.test_password)

        response = self.client.get(reverse('my_books'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You currently have no rented books.")
        self.assertQuerysetEqual(response.context['my_books_list'], [])


    def test_mybooks_view_rented_books_past_due(self):
        """
        If all books are past due, display appropriate message
        """
        self.client.login(username=self.test_username, password=self.test_password)

        time = timezone.now() + datetime.timedelta(days=-3)
        Book.objects.create(title='Test Book', rental_due_date=time)
        response = self.client.get(reverse('my_books'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You currently have no rented books.")
        self.assertQuerysetEqual(response.context['my_books_list'], [])
    


    def test_mybooks_view_rented_books_no_user(self):
        """
        If a book has no renting user, don't display it in my books
        """
        self.client.login(username=self.test_username, password=self.test_password)

        time = timezone.now() + datetime.timedelta(days=3)
        Book.objects.create(title='Test Book', rental_due_date=time)
        response = self.client.get(reverse('my_books'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You currently have no rented books.")
        self.assertQuerysetEqual(response.context['my_books_list'], [])


    def test_mybooks_view_rented_books_wrong_user(self):
        """
        Don't display books from another user
        """
        self.client.login(username=self.test_username, password=self.test_password)

        time = timezone.now() + datetime.timedelta(days=3)
        Book.objects.create(title='Test Book', rental_due_date=time, renting_user=User.objects.create())
        response = self.client.get(reverse('my_books'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You currently have no rented books.")
        self.assertQuerysetEqual(response.context['my_books_list'], [])
    

    def test_mybooks_view_some_books_rented(self):
        """
        Display books that are rented but not past due ones or for other users
        """
        self.client.login(username=self.test_username, password=self.test_password)

        time_1 = timezone.now() + datetime.timedelta(days=3)
        rented_book = Book.objects.create(title='Rented Book', rental_due_date=time_1, renting_user=self.user)
        no_user_book = Book.objects.create(title='No User Book', rental_due_date=time_1)
        time_2 = timezone.now() + datetime.timedelta(days=-3)
        past_due_book = Book.objects.create(title='Past Due Book', rental_due_date=time_2, renting_user=self.user)
        response = self.client.get(reverse('my_books'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['my_books_list'],
            [rented_book],
        )
    

    def test_books_view_multiple_books_rented(self):
        """
        Test multiple of my books with different due dates
        """
        self.client.login(username=self.test_username, password=self.test_password)

        time_1 = timezone.now() + datetime.timedelta(days=3)
        rented_book_1 = Book.objects.create(title='Test Book 1', rental_due_date=time_1, renting_user=self.user)
        time_2 = timezone.now() + datetime.timedelta(days=5)
        rented_book_2 = Book.objects.create(title='Test Book 2', rental_due_date=time_2, renting_user=self.user)
        response = self.client.get(reverse('my_books'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['my_books_list'],
            [rented_book_1, rented_book_2],
            ordered=False
        )


class BookDetailViewTests(TestCase):
    test_username = 'unit-test-user'
    test_email = 'unit@test.com'
    test_password = 'unittest'

    def setUp(self):
        self.user = User.objects.create_user(self.test_username, self.test_email, self.test_password)
    

    def test_book_detail_not_logged_in(self):
        """
        If not logged in, navigating to book detail should redirect with book detail as return
        """
        response = self.client.get(reverse('book_detail', args=(0,)))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/accounts/login/?next=/books/0')


    def test_book_detail_book_not_found(self):
        """
        If book is not found, return 404
        """
        self.client.login(username=self.test_username, password=self.test_password)

        response = self.client.get(reverse('book_detail', args=(0,)))
        self.assertEqual(response.status_code, 404)

    
    def test_book_detail_rented_book(self):
        """
        If someone else is renting the book, display due date and in use status
        """
        self.client.login(username=self.test_username, password=self.test_password)

        time = timezone.now() + datetime.timedelta(days=3)
        book = Book.objects.create(title='Test Book', rental_due_date=time)
        response = self.client.get(reverse('book_detail', args=(book.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Status: In use")
        self.assertNotContains(response, "Total rental charge")
    

    def test_book_detail_my_rented_book(self):
        """
        If I'm renting the book, display due date, in use status, and total rental charge
        """
        self.client.login(username=self.test_username, password=self.test_password)

        time = timezone.now() + datetime.timedelta(days=3)
        book = Book.objects.create(title='Test Book', rental_due_date=time, renting_user=self.user, days_rented=12)
        response = self.client.get(reverse('book_detail', args=(book.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Status: In use")
        self.assertContains(response, "Total rental charge")
    

    def test_book_detail_my_available_book(self):
        """
        If book was mine most recently but is past due date, show as available
        """
        self.client.login(username=self.test_username, password=self.test_password)

        time = timezone.now() + datetime.timedelta(days=-3)
        book = Book.objects.create(title='Test Book', rental_due_date=time, renting_user=self.user)
        response = self.client.get(reverse('book_detail', args=(book.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Status: <b>Available</b>")
        self.assertContains(response, "Days to borrow:")
        self.assertNotContains(response, "Total rental charge")
    

    def test_book_detail_available_book(self):
        """
        If book is past due date, show as available
        """
        self.client.login(username=self.test_username, password=self.test_password)

        time = timezone.now() + datetime.timedelta(days=-3)
        book = Book.objects.create(title='Test Book', rental_due_date=time)
        response = self.client.get(reverse('book_detail', args=(book.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Status: <b>Available</b>")
        self.assertContains(response, "Days to borrow:")

class RentTestCases(TestCase):
    test_username = 'unit-test-user'
    test_email = 'unit@test.com'
    test_password = 'unittest'

    def setUp(self):
        self.user = User.objects.create_user(self.test_username, self.test_email, self.test_password)

    
    def test_rent_not_logged_in(self):
        """
        If not logged in, posting to rent should redirect
        """
        response = self.client.post(reverse('rent', args=[0]), {'days_rented': '10'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/accounts/login/?next=/books/0/rent')
    

    def test_rent_book_not_found(self):
        """
        If book not found, return 404
        """
        self.client.login(username=self.test_username, password=self.test_password)

        response = self.client.post('/0/rent', {'days_rented': '10'})
        self.assertEqual(response.status_code, 404)

    
    def test_rent_book_already_rented(self):
        """
        If someone else is renting the book, return a 403 and a message
        This is not currently possible in the app flow, but want to test it in case
        """
        self.client.login(username=self.test_username, password=self.test_password)

        time = timezone.now() + datetime.timedelta(days=3)
        book = Book.objects.create(title='Test Book', rental_due_date=time, renting_user=User.objects.create())
        response = self.client.post(reverse('rent', args=[book.id]), data={'days_rented': '10'})
        self.assertEqual(response.status_code, 403)
    

    def test_rent_book_already_rented_by_me(self):
        """
        If I'm currently renting the book, return a 403 and a message
        This is not currently possible in the app flow, but want to test it in case
        """
        self.client.login(username=self.test_username, password=self.test_password)

        time = timezone.now() + datetime.timedelta(days=3)
        book = Book.objects.create(title='Test Book', rental_due_date=time, renting_user=User.objects.create())
        response = self.client.post(reverse('rent', args=[book.id]), {'days_rented': '10'})
        self.assertEqual(response.status_code, 403)
    

    def test_rent_available_book_past_due(self):
        """
        Rent a book that's available because it's past due
        """
        self.client.login(username=self.test_username, password=self.test_password)

        time = timezone.now() + datetime.timedelta(days=-3)
        book = Book.objects.create(title='Test Book', days_rented=1, rental_due_date=time, renting_user=User.objects.create())
        response = self.client.post(reverse('rent', args=[book.id]), {'days_rented': '10'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('book_detail', args=[book.id]))

        book = Book.objects.get(id=book.id)
        self.assertEqual(book.days_rented, 10)
        self.assertEqual(book.renting_user, self.user)
    

    def test_rent_available_book_null_user(self):
        """
        Rent a book that's available because its renting_user is null
        """
        self.client.login(username=self.test_username, password=self.test_password)

        time = timezone.now() + datetime.timedelta(days=3)
        book = Book.objects.create(title='Test Book', days_rented=1, rental_due_date=time)
        response = self.client.post(reverse('rent', args=[book.id]), {'days_rented': '10'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('book_detail', args=[book.id]))

        book = Book.objects.get(id=book.id)
        self.assertEqual(book.days_rented, 10)
        self.assertEqual(book.renting_user, self.user)
