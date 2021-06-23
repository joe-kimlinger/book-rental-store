from django.views import generic
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from .models import Book


# Create your views here.
class IndexView(generic.ListView):
    template_name = 'books/index.html'
    context_object_name = 'book_list'

    def get_queryset(self):
        return Book.objects.order_by('last_rented_date')[:5]


def my_books(request):
    my_books_list = Book.objects.filter(renting_user_id=request.user.id)
    context = {'my_books_list': my_books_list}
    return render(request, 'books/my_books.html', context)


class DetailView(generic.DetailView):
    model = Book
    template_name = 'books/book_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_id"] = self.request.user.id
        return context
