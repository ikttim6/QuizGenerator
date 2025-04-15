from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile  # Make sure UserProfile is imported


class UserRegistrationForm(UserCreationForm):
    USER_TYPES = (
        ('professor', 'Professor'),
        ('student', 'Student'),
    )

    user_type = forms.ChoiceField(choices=USER_TYPES, required=True)

    class Meta:
        model = User
        fields = ['username', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)

        if 'email' in self.cleaned_data:
            user.email = self.cleaned_data['email']

        if commit:
            user.save()
            profile = user.profile
            profile.user_type = self.cleaned_data['user_type']
            profile.save()

        return user
