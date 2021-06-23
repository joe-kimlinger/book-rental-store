from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.utils import timezone
from .models import Book


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'books/index.html'
    context_object_name = 'book_list'

    def get_queryset(self):
        return Book.objects.filter(rental_due_date__lt=timezone.now())


# Create your views here.
class MyBooksListView(generic.ListView):
    template_name = 'books/my_books.html'
    context_object_name = 'my_books_list'

    def get_queryset(self):
        return Book.objects\
                .filter(renting_user_id=self.request.user.id)\
                .filter(rental_due_date__gte=timezone.now())


class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'books/book_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_id"] = self.request.user.id
        return context

class RentSuccessView(generic.DetailView):
    model = Book
    template_name = 'books/rent_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_id"] = self.request.user.id
        return context

def rent(request, pk):
    book = get_object_or_404(Book, pk=pk)

    days_rented = int(request.POST['days_rented'])
    book.renting_user_id = request.user.id
    book.days_rented = days_rented
    book.rental_due_date = timezone.now() + timezone.timedelta(days=days_rented)
    book.save()
    
    return HttpResponseRedirect(reverse('book_detail', args=(book.id,)))
