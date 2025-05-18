# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User # Assuming you're using the default User model
from .models import UserProfile # Your UserProfile model
from django.db import transaction

class UserRegistrationForm(UserCreationForm):
    USER_TYPES = (
        ('professor', 'Professor'),
        ('student', 'Student'),
    )

    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(choices=USER_TYPES, required=True, widget=forms.Select)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    @transaction.atomic
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