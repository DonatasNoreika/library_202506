from django.shortcuts import render
from .models import Book, BookInstance, Author
from django.views import generic
from django.core.paginator import Paginator

# Create your views here.

def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='g').count()
    num_authors = Author.objects.all().count()
    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
    }
    return render(request, template_name="index.html", context=context)


def authors(request):
    authors = Author.objects.all()
    paginator = Paginator(authors, per_page=5)
    page_number = request.GET.get('page')
    paged_authors = paginator.get_page(page_number)
    context = {"authors": paged_authors}
    return render(request, template_name="authors.html", context=context)


def author(request, author_id):
    context = {"author": Author.objects.get(pk=author_id)}
    return render(request, template_name="author.html", context=context)


class BookListView(generic.ListView):
    model = Book
    template_name = "books.html"
    context_object_name = "books"
    paginate_by = 5


class BookDetailView(generic.DetailView):
    model = Book
    template_name = "book.html"
    context_object_name = "book"
