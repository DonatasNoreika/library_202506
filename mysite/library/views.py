from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import FormMixin
from django.shortcuts import render, redirect, reverse
from .models import Book, BookInstance, Author
from django.views import generic
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import password_validation
from .forms import BookReviewForm, UserUpdateForm, ProfileUpdateForm, InstanceCreateUpdateForm
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _

# Create your views here.

def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='g').count()
    num_authors = Author.objects.all().count()

    # Papildome kintamuoju num_visits, įkeliame jį į kontekstą.
    num_visits = request.session.get("num_visits", 1)
    request.session['num_visits'] = num_visits + 1

    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_visits": num_visits,
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


class BookDetailView(FormMixin, generic.DetailView):
    model = Book
    template_name = "book.html"
    context_object_name = "book"
    form_class = BookReviewForm

    def get_success_url(self):
        return reverse("book", kwargs={"pk": self.object.pk})

    # standartinis post metodo perrašymas, naudojant FormMixin, galite kopijuoti tiesiai į savo projektą.
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.book = self.object
        form.instance.reviewer = self.request.user
        form.save()
        return super().form_valid(form)


def search(request):
    query = request.GET.get('query')
    authors = Author.objects.filter(
        Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(description__icontains=query))
    books = Book.objects.filter(Q(title__icontains=query) | Q(summary__icontains=query) | Q(isbn__icontains=query) | Q(
        author__first_name__icontains=query) | Q(author__last_name__icontains=query))
    context = {
        "query": query,
        "authors": authors,
        "books": books,
    }
    return render(request, template_name="search.html", context=context)


class MyBookInstanceListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = "my_books.html"
    context_object_name = "instances"

    def get_queryset(self):
        return BookInstance.objects.filter(reader=self.request.user)


def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if not password == password2:
            messages.error(request, _("Passwords do not match!"))
            return redirect("register")
        else:
            try:
                password_validation.validate_password(password)
            except password_validation.ValidationError as errors:
                for error in errors:
                    messages.error(request, error)
                return redirect("register")

            if User.objects.filter(username=username).exists():
                messages.error(request, _('Username %s already exists!') % username)
                return redirect("register")
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, _('Email %s already exists!') % email)
                    return redirect("register")

        User.objects.create_user(username=username, email=email, password=password)
        messages.info(request, _('User %s registered!') % username)
        return redirect("login")

    if request.method == "GET":
        return render(request, template_name="register.html")


@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        new_email = request.POST['email']
        if new_email and request.user.email != new_email and User.objects.filter(email=new_email).exists():
            messages.error(request, _('Email %s already exists!') % new_email)
            return redirect("profile")
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.info(request, _("Profile updated"))
            return redirect("profile")

    context = {
        'u_form': UserUpdateForm(instance=request.user),
        'p_form': ProfileUpdateForm(instance=request.user.profile),
    }
    return render(request, template_name="profile.html", context=context)


class BookInstanceListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = BookInstance
    context_object_name = 'instances'
    template_name = 'instances.html'

    def test_func(self):
        return self.request.user.profile.is_employee


class BookInstanceDetailView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    model = BookInstance
    context_object_name = "instance"
    template_name = "instance.html"

    def test_func(self):
        return self.request.user.profile.is_employee


class BookInstanceCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = BookInstance
    template_name = "instance_form.html"
    form_class = InstanceCreateUpdateForm
    # fields = ['book', 'reader', 'due_back', 'status']
    success_url = "/library/instances/"

    def test_func(self):
        return self.request.user.profile.is_employee

    def form_valid(self, form):
        messages.success(self.request, _("Book Instance created"))
        return super().form_valid(form)


class BookInstanceUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = BookInstance
    template_name = "instance_form.html"
    form_class = InstanceCreateUpdateForm
    # fields = ['book', 'reader', 'due_back', 'status']
    # success_url = "/library/instances/"

    def get_success_url(self):
        return reverse("instance", kwargs={"pk": self.object.pk})

    def test_func(self):
        return self.request.user.profile.is_employee

    def form_valid(self, form):
        messages.success(self.request, _("Book Instance updated"))
        return super().form_valid(form)


class BookInstanceDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = BookInstance
    template_name = "instance_delete.html"
    context_object_name = "instance"
    success_url = "/library/instances/"

    def test_func(self):
        return self.request.user.profile.is_employee

    def form_valid(self, form):
        messages.success(self.request, _("Book Instance deleted"))
        return super().form_valid(form)
