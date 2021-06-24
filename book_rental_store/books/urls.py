from django.urls import path

from . import views


urlpatterns = [
    path('', views.BooksView.as_view(), name='books'),
    path('mybooks', views.MyBooksListView.as_view(), name='my_books'),
    path('<int:pk>/rent', views.rent, name='rent'),
    path('<int:pk>', views.BookDetailView.as_view(), name='book_detail')
]
