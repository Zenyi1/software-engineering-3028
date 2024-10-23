from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import *  # Import your custom User model

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Keep email as required
    first_name = forms.CharField(max_length=30, required=True)  # First name
    last_name = forms.CharField(max_length=30, required=True)  # Last name

    class Meta:
        model = User  # Use your custom User model
        fields = ("username", "first_name", "last_name", "email", "password1", "password2", "role")  # Include first and last names

    def clean_email(self):
        # This method will be called automatically to clean the email field
        email = self.cleaned_data.get("email")
        if email and not email.endswith('@abdn.ac.uk'):
            raise ValidationError(_('Email must be an @abdn.ac.uk address.'))
        return email

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
