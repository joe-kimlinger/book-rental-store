from django.test import TestCase
from django.utils import timezone
import datetime

from .models import Book


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
