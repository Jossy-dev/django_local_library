import datetime
from itertools import chain

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from catalog.forms import RenewBookForm, UpdateUserForm, UpdateProfileForm, NewUserForm, BookCreateForm
from catalog.models import Author
from . import forms
# Create your views here.
from .models import Book, BookInstance, Genre, Language, Profile


def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    books = Book.objects.order_by('title')[:8]
    latest = Book.objects.order_by('-date_added')[:4]
    authors = Author.objects.order_by('first_name')[:8]
    genres = Genre.objects.order_by('name')[:8]

    context = {
        'books': books,
        'latest': latest,
        'authors': authors,
        'genres': genres,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 12
    context_object_name = 'book_list'  # your own name for the list as a template variable
    template_name = 'catalog/book_list.html'  # Specify your own template name/location

    def get_context_data(self, *args, **kwargs):
        borrowed_id = []
        context = super(BookListView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            borrowed = BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o')
            for book_id in borrowed:
                borrowed_id.append(book_id.book.id)
            context['borrowed_books_id'] = borrowed_id
        return context


class BookDetailView(generic.DetailView):
    model = Book

    def get_context_data(self, *args, **kwargs):
        context = super(BookDetailView, self).get_context_data(**kwargs)
        copies = self.get_object().bookinstance_set.filter(status='a').count()
        context['copies'] = copies

        return context


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 12

    context_object_name = 'author_list'

    queryset = Author.objects.all()

    template_name = 'templates/catalog/author_list.html'


class AuthorDetailView(generic.DetailView):
    model = Author


class GenreListView(generic.ListView):
    model = Genre
    paginate_by = 12
    context_object_name = 'genre_list'

    queryset = Genre.objects.all()

    template_name = 'catalog/genre_list.html'


class GenreDetailView(generic.DetailView):
    model = Genre


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 12

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LibrarianBorrowedBooksListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    context_object_name = 'librarian_list';
    template_name = 'catalog/librarian_books_borrowed_list.html'
    paginate_by = 15

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

    def get_context_data(self, *args, **kwargs):
        context = super(LibrarianBorrowedBooksListView, self).get_context_data(**kwargs)
        return context


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('librarian-list'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__'  # Not recommended (potential security issue if more fields added)


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


# class BookCreate(CreateView):
#     model = Book
#     fields = ['title', 'image', 'author', 'summary', 'date_added', 'isbn', 'genre', 'language']
class BookCreate(CreateView):
    form_class = BookCreateForm
    model = Book


class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'  # Not recommended (potential security issue if more fields added)
    # template_name_suffix = 'Update'


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    # template_name_suffix = 'Delete'


class GenreCreate(CreateView):
    model = Genre
    fields = '__all__'
    success_url = reverse_lazy('book-create')


class GenreUpdate(UpdateView):
    model = Genre
    fields = '__all__'  # Not recommended (potential security issue if more fields added)
    # template_name_suffix = 'Update'


class GenreDelete(DeleteView):
    model = Genre
    success_url = reverse_lazy('books')
    # template_name_suffix = 'Delete'


class LanguageCreate(CreateView):
    model = Language
    fields = '__all__'
    success_url = reverse_lazy('book-create')


def search(request):
    search_term = request.GET.get('q', None)

    if search_term:
        author_f = Author.objects.filter(first_name__icontains=search_term)
        author_l = Author.objects.filter(last_name__icontains=search_term)
        book_t = Book.objects.filter(title__icontains=search_term)
        genre_n = Genre.objects.filter(name__iexact=search_term)

        found_entries = list(
            sorted(
                chain(author_f, author_l, book_t, genre_n),
                key=lambda objects: objects.pk
            ))
        page = request.GET.get('page', 1)

        paginator = Paginator(found_entries, 10)
        try:
            found_entries = paginator.page(page)
        except PageNotAnInteger:
            found_entries = paginator.page(1)
        except EmptyPage:
            found_entries = paginator.page(paginator.num_pages)

        return render(request, 'catalog/search_result_all.html',
                      {'query_string': search_term, 'found_entries': found_entries},
                      )

    else:
        return HttpResponse('Please enter a search term')


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid():
            print("User form is valid")
        else:
            print("user form not valid")
        if profile_form.is_valid():
            print("Profile form is valid")
        else:
            print("Profile form not valid")

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='profile-detail')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'catalog/profile.html', {'user_form': user_form, 'profile_form': profile_form})


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect(to='users-profile')
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="catalog/register.html", context={"register_form": form})


class RecommendedListView(LoginRequiredMixin, generic.ListView):
    model = Profile
    order_by = 'date_added'
    context_object_name = 'recommended'
    template_name = 'catalog/recommended.html'

    def get_queryset(self):
        return Profile.objects.get(user=self.request.user)


def profile_detail(request):
    return render(request, 'catalog/profile_detail.html')


@login_required
def borrow_book_action(request):
    book_id = request.POST.get('id')
    user = request.user
    due_date = datetime.date.today() + datetime.timedelta(weeks=1)
    if request.method == 'POST':
        try:
            book_instance = Book.objects.get(id=book_id)

            book_exists = BookInstance.objects.filter(
                book=book_instance,
                borrower=user
            ).exists()

            if book_exists:
                return JsonResponse({
                    "completed": False
                })

            book_borrow_instance = BookInstance.objects.create(
                book=book_instance,
                due_back=due_date,
                borrower=user,
                status="o"
            )

            return JsonResponse({
                "completed": True
            })

        except Book.DoesNotExist:
            print("This book does not exist")
            raise Http404()


def return_book(request):
    instance_id = request.POST.get('id')

    if request.method == 'POST':
        # book_instance = BookInstance.objects.get(id=instance_id)
        try:
            BookInstance.objects.filter(pk=instance_id).update(status="a")

            return JsonResponse({
                "completed": True
            })

        except BookInstance.DoesNotExist:
            print("This book instance does not exist")
            raise Http404()
