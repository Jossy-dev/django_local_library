from django.urls import path, include
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
]

urlpatterns += [
    path('genres/', views.GenreListView.as_view(), name='genres'),
    path('genre/<int:pk>', views.GenreDetailView.as_view(), name='genre-detail'),
]

urlpatterns += [
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]

urlpatterns += [
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),
]

urlpatterns += [
    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
    path('book/create/addlanguage/', views.LanguageCreate.as_view(), name='language-create'),
    path('genre/create/addgenre/', views.GenreCreate.as_view(), name='genre-create'),
    path('genre/<int:pk>/update/', views.GenreUpdate.as_view(), name='genre-update'),
    path('genre/<int:pk>/delete/', views.GenreDelete.as_view(), name='genre-delete'),
]

urlpatterns += [
    path('search/', views.search, name='search_all_result'),
]

urlpatterns += [
    path('profile/', views.profile, name='users-profile'),
    path('register/', views.register_request, name="register"),
    path('recommended/', views.RecommendedListView.as_view(), name='recommended'),
    path('profiledetail/', views.profile_detail, name='profile-detail'),
    path('borrow/', views.borrow_book_action, name='borrow'),
    path("select2/", include("django_select2.urls")),
]

urlpatterns += staticfiles_urlpatterns()
