from django.contrib import admin
from .models import Book, BookType

# Register your models here.
admin.site.register(Book)
admin.site.register(BookType)
