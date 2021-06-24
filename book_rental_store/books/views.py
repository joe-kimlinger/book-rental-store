from django.http.response import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.utils import timezone
from .models import Book
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


class BooksView(generic.ListView):
    template_name = 'books/books.html'
    context_object_name = 'books_list'

    def get_queryset(self):
        return Book.objects.filter(Q(rental_due_date__lt=timezone.now())
                                    | Q(renting_user__isnull=True))


class MyBooksListView(LoginRequiredMixin, generic.ListView):
    template_name = 'books/my_books.html'
    context_object_name = 'my_books_list'

    def get_queryset(self):
        print(self.request.user)
        return Book.objects\
                .filter(renting_user=self.request.user.id)\
                .filter(rental_due_date__gte=timezone.now())\
                .order_by('rental_due_date')


class BookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Book
    template_name = 'books/book_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@login_required
def rent(request, pk):
    
    book = get_object_or_404(Book, pk=pk)

    if not book.available():
        message = ''
        if book.renting_user == request.user:
            message = "You're already renting this book."
        else:
            message = "Sorry, someone else is renting this right now."
        
        if message:
            return HttpResponseForbidden(message)

    book.renting_user = request.user
    
    days_rented = int(request.POST['days_rented'])
    book.days_rented = days_rented
    book.rental_due_date = timezone.now() + timezone.timedelta(days=days_rented)
    book.save()
    
    return HttpResponseRedirect(reverse('book_detail', args=(book.id,)))
