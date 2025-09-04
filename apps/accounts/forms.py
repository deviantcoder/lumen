from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm
)
from django.contrib.auth import get_user_model


User = get_user_model()


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].widget.attrs.update({'placeholder': 'Enter your username or email'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Enter your password'})


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'email', 'username', 'full_name', 'password1', 'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].widget.attrs.update({'placeholder': 'Enter your email'})
        self.fields['username'].widget.attrs.update({'placeholder': 'Choose a username'})
        self.fields['full_name'].widget.attrs.update({'placeholder': 'Your full name'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Create a password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Repeat the password'})
