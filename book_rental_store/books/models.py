from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class BookType(models.Model):
    book_type = models.CharField(max_length=50)
    rental_rate = models.DecimalField(max_digits=12, decimal_places=2, default=1.50)
    min_days = models.PositiveIntegerField(default=0)
    min_days_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return self.book_type


class Book(models.Model):
    title = models.CharField(max_length=75)
    author = models.CharField(max_length=75)
    book_type = models.ForeignKey('BookType', on_delete=models.PROTECT)
    days_rented = models.PositiveIntegerField(blank=True, null=True)
    rental_due_date = models.DateTimeField(default=timezone.now)
    renting_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title

    def days_remaining(self):
        delta = self.rental_due_date - timezone.now()
        return max(delta.days, 0)

    def rental_charge(self):
        if self.days_rented == None:
            raise Exception('Error: days_rented is undefined')
            
        rental_charge = self.book_type.min_days * self.book_type.min_days_rate + \
            self.book_type.rental_rate * max(0, self.days_rented - self.book_type.min_days)
        return max(rental_charge, 0)
    
    def minimum_charge(self):
        return self.book_type.min_days * self.book_type.min_days_rate
    
    def available(self):
        return (self.rental_due_date < timezone.now()) or not self.renting_user
