from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from .models import Book, Author, BookInstance, Genre, Language
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages

import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from catalog.forms import RenewBookForm, UpdateUserForm, UpdateProfileForm, NewUserForm

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author
from django.views import generic

from django.contrib.auth import login


def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Genre's that contain letter 'e'
    genre_e = Genre.objects.filter(name__icontains='e').count

    # Book's that contain letter 'a'
    book_a = Book.objects.filter(title__icontains='a').count

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'genre_e': genre_e,
        'book_a': book_a,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book

    context_object_name = 'book_list'  # your own name for the list as a template variable

    queryset = Book.objects.all()  # List all books

    template_name = 'templates/catalog/book_list.html'  # Specify your own template name/location


# We can override objects when using class-based views
#  def get_queryset(self):
#         return Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war

class BookDetailView(generic.DetailView):
    model = Book;


class AuthorListView(generic.ListView):
    model = Author;
    paginate_by = 5

    context_object_name = 'author_list';

    queryset = Author.objects.all();

    template_name = 'templates/catalog/author_list.html'


class AuthorDetailView(generic.DetailView):
    model = Author;


class GenreListView(generic.ListView):
    model = Genre;
    paginate_by = 5
    order_by = 'name'
    context_object_name = 'genre_list';

    queryset = Genre.objects.all();

    template_name = 'templates/catalog/genre_list.html'


class GenreDetailView(generic.DetailView):
    model = Genre;

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 5

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LibrarianBorrowedBooksListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    context_object_name = 'librarian_list';
    template_name = 'catalog/librarian_books_borrowed_list.html'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


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


class BookCreate(CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    # template_name_suffix = 'New'


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


class LanguageCreate(CreateView):
    model = Language
    fields = '__all__'
    success_url = reverse_lazy('book-create')



def search(request):
    search_term = request.GET.get('q', None)

    if search_term:
        author_f = list(Author.objects.filter(first_name__icontains=search_term))
        author_l = list(Author.objects.filter(last_name__icontains=search_term))
        book_t = list(Book.objects.filter(title__icontains=search_term))
        genre_n = list(Genre.objects.filter(name__iexact=search_term))
        found_entries = set(author_f) | set(author_l) | set(book_t) | set(genre_n)
        final = found_entries

        return render(request, 'catalog/search_result_all.html',
                      {'query_string': search_term, 'found_entries': final},
                      )

    else:
        return HttpResponse('Please enter a search term')


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users-profile')
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
            messages.success(request, "Registration successful." )
            return redirect(to='users-profile')
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render (request=request, template_name="catalog/register.html", context={"register_form":form})