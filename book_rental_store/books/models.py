from django.db import models
from django.utils import timezone

# Create your models here.

class Book(models.Model):
    title = models.TextField()
    author = models.TextField()
    rental_start_date = models.DateTimeField(default=timezone.now)
    rental_due_date = models.DateTimeField(default=timezone.now)
    rental_rate = models.DecimalField(max_digits=12, decimal_places=2, default=1.00)
    renting_user_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title

    def days_remaining(self):
        print(self.rental_due_date)
        print(self.rental_start_date)
        delta = self.rental_due_date - timezone.now()
        return delta.days

    def rental_charge(self):
        delta = self.rental_due_date - self.rental_start_date
        days_rented = delta.days + min(1, delta.seconds)
        return days_rented * self.rental_rate
    
    def past_due(self):
        return self.rental_due_date < timezone.now()
