from django.db import models
from django.utils import timezone

# Create your models here.

class Book(models.Model):
    rented = models.BooleanField(default=False)
    last_rented_date = models.DateTimeField(default=timezone.now)
