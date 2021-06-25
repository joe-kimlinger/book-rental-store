from django.http.response import HttpResponseRedirect
from django.test import TestCase, client
from django.contrib.auth.models import User
from django.urls.base import reverse
from django.utils import timezone
import datetime

from .models import Book, BookType


# Helper function for creating a book with various properties
def create_book_helper(title='', day_diff=None, renting_user='blank', book_type=None, days_rented=None):
    
        time=timezone.now()
        if day_diff:
            time = timezone.now() + datetime.timedelta(days=day_diff)

        
        if not book_type:
            book_type = BookType.objects.create()
            book_type.save()

        if renting_user == 'blank':
            renting_user = None

        
        return Book.objects.create(title=title, rental_due_date=time, renting_user=renting_user, 
                                   book_type=book_type, days_rented=days_rented)


####### MODEL UNIT TESTS ##########

class BookTypeModelTests(TestCase):

    def test_str_conversion(self):
        """
        check that __str__() returns book type
        """
        type = 'My Type'
        book_type = BookType(book_type=type)
        self.assertEqual(str(book_type), type)


class BookModelTests(TestCase): # pragma: no cover

    def test_days_remaining_with_past_due_date(self):
        """
        days_remaining() should return 0 if the due_date is in the past
        """
        past_due_book = create_book_helper(day_diff=-3) 

        self.assertEqual(past_due_book.days_remaining(), 0)
    

    def test_days_remaining_on_due_date(self):
        """
        days_remaining() should return 0 if the due_date less that 24 hours 
        from the current date
        """
        time = timezone.now() + datetime.timedelta(hours=12)
        almost_due_book = Book(rental_due_date=time, book_type=BookType())

        self.assertEqual(almost_due_book.days_remaining(), 0)


    def test_days_remaining_before_due_date(self):
        """
        check that days_remaining() lines up with configured delta
        """
        delta = 12
        time = timezone.now() + datetime.timedelta(days=delta, minutes=1)
        almost_due_book = Book(rental_due_date=time, book_type=BookType())
        
        self.assertEqual(almost_due_book.days_remaining(), delta)
    

    def test_rental_charge_empty_days_rented(self):
        """
        check that rental_charge() with emtpy days_rented raises exception
        """
        book = create_book_helper() 
        
        with self.assertRaises(Exception) as exc:
            book.rental_charge()

        self.assertEqual(str(exc.exception), 'Error: days_rented is undefined')

            
    def test_rental_charge_past_due_date(self):
        """
        check that rental_charge() still gives total rental charge after due date
        """
        past_due_book = create_book_helper(day_diff=-6,  days_rented=10) 

        self.assertEqual(past_due_book.rental_charge(), 15.00)


    def test_rental_charge_before_due_date(self):
        """
        check that rental_charge() still gives correct rental charge before due date
        """
        days = 10
        rate = 1.6
        book_type = BookType.objects.create(rental_rate=rate)
        almost_due_book = create_book_helper('Title', -6, days_rented=days, book_type=book_type)

        self.assertEqual(almost_due_book.rental_charge(), days * book_type.rental_rate)
    

    def test_rental_charge_different_book_type(self):
        """
        check that rental_charge() gives different charges for different book types
        """
        book_type_1 = BookType.objects.create(book_type="Novel", rental_rate=4.50)
        book_type_2 = BookType.objects.create(book_type="Regular", rental_rate=3.50)
        days_rented = 10
        book_1 = create_book_helper('Title', days_rented=days_rented, book_type=book_type_1)
        book_2 = create_book_helper('Title', days_rented=days_rented, book_type=book_type_2)
        self.assertNotEqual(book_1.rental_charge(), book_2.rental_charge())
    

    def test_rental_charge_min_days_book_type(self):
        """
        check that rental_charge() calulcates rental charge correct for min charge type
        """
        days_rented = 10
        min_days = 2
        min_days_rate = 5
        rental_rate = 4.50
        book_type = BookType.objects.create(book_type="Novel", rental_rate=rental_rate, 
                                              min_days=min_days, min_days_rate=min_days_rate)
        book = create_book_helper('Title', days_rented=days_rented, book_type=book_type)
        self.assertEqual(book.rental_charge(), min_days_rate * min_days + rental_rate * (days_rented - min_days))
    

    def test_rental_charge_under_min_days(self):
        """
        check that rental_charge() gives minimum charge if rental days is under min_days
        """
        days_rented = 3
        min_days = 5
        min_days_rate = 5
        rental_rate = 4.50
        book_type = BookType.objects.create(book_type="Novel", rental_rate=rental_rate, 
                                              min_days=min_days, min_days_rate=min_days_rate)
        book = create_book_helper('Title', days_rented=days_rented, book_type=book_type)
        self.assertEqual(book.rental_charge(), min_days_rate * min_days)


    def test_rental_charge_negative_min_days_rate(self):
        """
        check that rental_charge() does not give negatives for rental rate
        """
        days_rented = 3
        rental_rate = -4.50
        book_type = BookType.objects.create(book_type="Novel", rental_rate=rental_rate)
        book = create_book_helper('Title', days_rented=days_rented, book_type=book_type)
        self.assertEqual(book.rental_charge(), 0)


    def test_rental_charge_negative_min_days_rate(self):
        """
        check that rental_charge() does not give negatives for min days rate
        This is a misconfigured book type because it's not charging for the min_days period
        If this occurs, we at least don't want to have a negative charge, no charge is fine
        """
        days_rented = 3
        min_days = 5
        min_days_rate = -5.50
        rental_rate = 4.50
        book_type = BookType.objects.create(book_type="Novel", rental_rate=rental_rate, 
                                              min_days=min_days, min_days_rate=min_days_rate)
        book = create_book_helper('Title', days_rented=days_rented, book_type=book_type)
        self.assertEqual(book.rental_charge(), 0)


    def test_available_past_due_date_null_user(self):
        """
        check that available() returns true with a null user
        """
        past_due_book = create_book_helper(day_diff=-1)

        self.assertTrue(past_due_book.available())


    def test_available_before_due_date_null_user(self):
        """
        check that available() returns true with a null user
        """
        past_due_book = create_book_helper(days_rented=1)

        self.assertTrue(past_due_book.available())


    def test_available_before_due_date_with_user(self):
        """
        check that available() returns false with a user and before the due date
        """
        past_due_book = create_book_helper('Test Book', 1, User.objects.create())

        self.assertFalse(past_due_book.available())


    def test_available_past_due_date_with_user(self):
        """
        check that available() returns true with a user and past the due date
        """
        past_due_book = create_book_helper('Test Book', -1, User.objects.create())

        self.assertTrue(past_due_book.available())


    def test_str_conversion(self):
        """
        check that __str__() returns book title
        """
        title = 'My Title'
        book = create_book_helper(title)

        self.assertEqual(str(book), title)


    def test_deleting_user_makes_book_available(self):
        """
        check that removing a user that's renting a book makes the book available
        """
        user = User.objects.create()
        book = create_book_helper(day_diff=3, renting_user=user)

        book = Book.objects.get(id=book.id)
        self.assertFalse(book.available())

        User.objects.get(id=user.id).delete()

        book = Book.objects.get(id=book.id)
        self.assertTrue(book.available())

    
    def test_deleting_type_throws_exception(self):
        """
        check removing a book type associated with a book throws an exception
        """
        book_type = BookType.objects.create()
        create_book_helper(book_type=book_type)

        with self.assertRaises(Exception) as exc:
            BookType.objects.get(id=book_type.id).delete()


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
        create_book_helper('Test Book', 3, User.objects.create())
        response = self.client.get(reverse('books'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are currently no books available.")
        self.assertQuerysetEqual(response.context['books_list'], [])
    

    def test_books_view_books_available(self):
        """
        Display books that are available
        """
        available_book = create_book_helper('Test Book', -3)
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
        rented_book = create_book_helper('Rented Book', 3, new_user)
        available_book_1 = create_book_helper('Available Book 1', 3)
        available_book_2 = create_book_helper('Available Book 2', -3, new_user)
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
        available_book_1 = create_book_helper('Test Book 1', -3)
        available_book_2 = create_book_helper('Test Book 2', 5)
        response = self.client.get(reverse('books'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['books_list'],
            [available_book_1, available_book_2],
            ordered=False
        )


class MyBooksViewTests(TestCase):
    username_test = 'unit-test-user'
    email_test = 'unit@test.com'
    password_test = 'unittest'

    def setUp(self):
        self.user = User.objects.create_user(self.username_test, self.email_test, self.password_test)


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
        self.client.force_login(self.user)

        response = self.client.get(reverse('my_books'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You currently have no rented books.")
        self.assertQuerysetEqual(response.context['my_books_list'], [])


    def test_mybooks_view_rented_books_past_due(self):
        """
        If all books are past due, display appropriate message
        """
        self.client.force_login(self.user)

        create_book_helper('Test Book', -3)
        response = self.client.get(reverse('my_books'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You currently have no rented books.")
        self.assertQuerysetEqual(response.context['my_books_list'], [])
    


    def test_mybooks_view_rented_books_no_user(self):
        """
        If a book has no renting user, don't display it in my books
        """
        self.client.force_login(self.user)

        create_book_helper('Test Book', 3)
        response = self.client.get(reverse('my_books'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You currently have no rented books.")
        self.assertQuerysetEqual(response.context['my_books_list'], [])


    def test_mybooks_view_rented_books_wrong_user(self):
        """
        Don't display books from another user
        """
        self.client.force_login(self.user)

        create_book_helper('Test Book', 3, User.objects.create())
        response = self.client.get(reverse('my_books'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You currently have no rented books.")
        self.assertQuerysetEqual(response.context['my_books_list'], [])
    

    def test_mybooks_view_some_books_rented(self):
        """
        Display books that are rented but not past due ones or for other users
        """
        self.client.force_login(self.user)

        rented_book = create_book_helper('Rented Book', 3, self.user)
        no_user_book = create_book_helper('No User Book', 3, User.objects.create())
        past_due_book = create_book_helper('Past Due Book', -3, self.user)

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
        self.client.force_login(self.user)

        rented_book_1 = create_book_helper('Test Book 1', 3, self.user)
        rented_book_2 = create_book_helper('Test Book 2', 5, self.user)

        response = self.client.get(reverse('my_books'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['my_books_list'],
            [rented_book_1, rented_book_2],
            ordered=False
        )


class BookDetailViewTests(TestCase):
    username_test = 'unit-test-user'
    email_test = 'unit@test.com'
    password_test = 'unittest'

    def setUp(self):
        self.user = User.objects.create_user(self.username_test, self.email_test, self.password_test)


    def test_book_detail_book_not_found(self):
        """
        If book is not found, return 404
        """
        response = self.client.get(reverse('book_detail', args=(0,)))
        self.assertEqual(response.status_code, 404)

    
    def test_book_detail_rented_book(self):
        """
        If someone else is renting the book, display due date and in use status
        """
        self.client.force_login(self.user)

        book = create_book_helper('Test Book', 3, User.objects.create())

        response = self.client.get(reverse('book_detail', args=(book.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Status: In use")
        self.assertNotContains(response, "Total rental charge")
    

    def test_book_detail_past_due_empty_user(self):
        """
        If the book is past due but there's an empty renting_user value, it's available
        """
        self.client.force_login(self.user)

        book = create_book_helper('Test Book', 3)

        response = self.client.get(reverse('book_detail', args=(book.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Status: <b>Available</b>")
        self.assertContains(response, "Days to borrow:")
        self.assertNotContains(response, "Total rental charge")
    

    def test_book_detail_past_due_empty_user_not_logged_in(self):
        """
        If the book is past due but there's an empty renting_user value, it's available
        """
        book = create_book_helper('Test Book', 3)

        response = self.client.get(reverse('book_detail', args=(book.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Days to borrow:")
        self.assertContains(response, 'Login</a> to rent this book!')


    def test_book_detail_my_rented_book(self):
        """
        If I'm renting the book, display due date, in use status, and total rental charge
        """
        self.client.force_login(self.user)

        book = create_book_helper('Test Book', 3, self.user, days_rented=12)

        response = self.client.get(reverse('book_detail', args=(book.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Status: In use")
        self.assertContains(response, "Total rental charge")
    

    def test_book_detail_my_available_book(self):
        """
        If book was mine most recently but is past due date, show as available
        """
        self.client.force_login(self.user)

        book = create_book_helper('Test Book', -3, self.user)

        response = self.client.get(reverse('book_detail', args=(book.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Status: <b>Available</b>")
        self.assertContains(response, "Days to borrow:")
        self.assertNotContains(response, "Total rental charge")
    

    def test_book_detail_available_book(self):
        """
        If book is past due date, show as available
        """
        self.client.force_login(self.user)

        book = create_book_helper('Test Book', -3, User.objects.create())

        response = self.client.get(reverse('book_detail', args=(book.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Status: <b>Available</b>")
        self.assertContains(response, "Days to borrow:")
    

    def test_book_detail_shows_right_rental_rate(self):
        """
        Show the rental rate related to the book type
        """
        book_type = BookType.objects.create(book_type='Test type', rental_rate=5.50)
        book = create_book_helper('Test Book', -3, User.objects.create(), book_type)

        response = self.client.get(reverse('book_detail', args=(book.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "thereafter")
        self.assertNotContains(response, "Minimum charge:")
    

    def test_book_detail_shows_right_rental_rate_min_days(self):
        """
        Show the rental rate related to the book type
        """
        book_type = BookType.objects.create(book_type='Test type', rental_rate=5.50,
                                            min_days=5, min_days_rate=3.50)
        book = create_book_helper('Test Book', -3, User.objects.create(), book_type)

        response = self.client.get(reverse('book_detail', args=(book.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "thereafter")
        self.assertContains(response, "Minimum charge:")


class RentTestCases(TestCase):
    username_test = 'unit-test-user'
    email_test = 'unit@test.com'
    password_test = 'unittest'

    def setUp(self):
        self.user = User.objects.create_user(self.username_test, self.email_test, self.password_test)

    
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
        self.client.force_login(self.user)

        response = self.client.post('/0/rent', {'days_rented': '10'})
        self.assertEqual(response.status_code, 404)

    
    def test_rent_book_already_rented(self):
        """
        If someone else is renting the book, return a 403 and a message
        This is not currently possible in the app flow, but want to test it in case
        """
        self.client.force_login(self.user)

        time = timezone.now() + datetime.timedelta(days=3)
        book = create_book_helper('Test Book', 3, User.objects.create())
        response = self.client.post(reverse('rent', args=[book.id]), data={'days_rented': '10'})
        self.assertEqual(response.status_code, 403)
    

    def test_rent_book_already_rented_by_me(self):
        """
        If I'm currently renting the book, return a 403 and a message
        This is not currently possible in the app flow, but want to test it in case
        """
        self.client.force_login(self.user)

        book = create_book_helper('Test Book', 3, self.user)
        response = self.client.post(reverse('rent', args=[book.id]), {'days_rented': '10'})
        self.assertEqual(response.status_code, 403)
    

    def test_rent_available_book_past_due(self):
        """
        Rent a book that's available because it's past due
        """
        self.client.force_login(self.user)

        book = create_book_helper('Test Book', -3, User.objects.create(), days_rented=1)

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
        self.client.force_login(self.user)

        book = create_book_helper('Test Book', -3, days_rented=1)
        response = self.client.post(reverse('rent', args=[book.id]), {'days_rented': '10'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('book_detail', args=[book.id]))

        book = Book.objects.get(id=book.id)
        self.assertEqual(book.days_rented, 10)
        self.assertEqual(book.renting_user, self.user)
