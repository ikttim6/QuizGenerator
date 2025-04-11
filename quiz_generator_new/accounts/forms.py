from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


class UserRegistrationForm(UserCreationForm):
    USER_TYPES = (
        ('professor', 'Professor'),
        ('student', 'Student'),
    )

    user_type = forms.ChoiceField(choices=USER_TYPES, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                user_type=self.cleaned_data['user_type']
            )

        return user
