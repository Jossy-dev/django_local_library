import datetime

from cloudinary.forms import CloudinaryFileField
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import CheckboxSelectMultiple
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView

from . import models
from .models import Profile, BookInstance, Genre, Book
from django_select2 import forms as s2forms


class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100,
                                 required=True,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100,
                                required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


# class GenreWidget(s2forms.ModelSelect2Widget):
#     search_fields = [
#         "name__icontains",
#     ]


class UpdateProfileForm(forms.ModelForm):
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))
    nationality = forms.CharField(max_length=100, help_text='Enter your nationality',
                                  widget=forms.TextInput(attrs={'class': 'form-control'})),

    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'favourite_genre', 'nationality']


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Check if a date is not in the past.
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # Check if a date is in the allowed range (+4 weeks from today).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class BookInstanceForm(forms.ModelForm):
    class Meta:
        model = BookInstance
        fields = ['id', 'book', 'due_back', 'borrower', 'status']


class BookCreateForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'image', 'author', 'summary', 'date_added', 'isbn', 'genre', 'language']
        widgets = {
            'date_added': forms.DateInput()
        }
