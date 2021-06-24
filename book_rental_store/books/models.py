from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Book(models.Model):
    title = models.TextField()
    author = models.TextField()
    days_rented = models.PositiveIntegerField(blank=True, null=True)
    rental_due_date = models.DateTimeField(default=timezone.now)
    rental_rate = models.DecimalField(max_digits=12, decimal_places=2, default=1.00)
    renting_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title

    def days_remaining(self):
        delta = self.rental_due_date - timezone.now()
        return max(delta.days, 0)

    def rental_charge(self):
        if self.days_rented == None:
            raise Exception('Error: days_rented is undefined')
            
        return max(self.days_rented * self.rental_rate, 0)
    
    def past_due(self):
        return self.rental_due_date < timezone.now()
