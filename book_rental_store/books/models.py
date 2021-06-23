from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator 


# Create your models here.

class Book(models.Model):
    title = models.TextField()
    author = models.TextField()
    days_rented = models.PositiveIntegerField(blank=True, null=True)
    rental_due_date = models.DateTimeField(default=timezone.now)
    rental_rate = models.DecimalField(max_digits=12, decimal_places=2, default=1.00)
    renting_user_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title

    def days_remaining(self):
        delta = self.rental_due_date - timezone.now()
        return max(delta.days, 0)

    def rental_charge(self):
        return self.days_rented * self.rental_rate
    
    def past_due(self):
        return self.rental_due_date < timezone.now()
