from django.urls import path

from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('books/mybooks', views.my_books, name='my_books'),
    path('<int:pk>', views.DetailView.as_view(), name='book_detail')
]
