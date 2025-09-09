from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout, get_user_model, login
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import generic
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode

from .forms import LoginForm, SignupForm
from .utils import send_activation_email
from .tokens import account_activation_token_generator


User = get_user_model()


class LoginUserView(LoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)

        user = self.request.user

        if user.account_activated:
            messages.success(self.request, 'Welcome back!')
            return redirect(self.get_success_url())
        else:
            messages.warning(self.request, 'Please verify your email before logging in.')
            logout(self.request)
            return redirect(reverse_lazy('home'))
    
    def form_invalid(self, form):
        messages.warning(self.request, 'Invalid email, username or password.')
        return super().form_invalid(form)


class LogoutUserView(LogoutView):
    next_page = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You've been logged out.")
        return super().dispatch(request, *args, **kwargs)


class SignupUserView(generic.CreateView):
    template_name = 'accounts/signup.html'
    form_class = SignupForm
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse_lazy('home'))

        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance

        if user:
            send_activation_email(user)
            return render(
                self.request,
                'accounts/activation/activation_email_sent.html',
                context={'sent': True}
            )
        return response
        
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.warning(self.request, f'{field.capitalize()}: {error}.')
        return super().form_invalid(form)


def activate_account(request, uidb64, token):
    if request.user.is_authenticated and request.user.email_verified:
        return redirect(reverse_lazy('home'))

    try:
        public_id_bytes = urlsafe_base64_decode(uidb64)
        public_id = public_id_bytes.decode('utf-8')
        
        user = get_object_or_404(User, public_id=public_id)
    except (User.DoesNotExist, ValueError, UnicodeDecodeError):
        user = None

    if user is not None and account_activation_token_generator.check_token(user, token):
        user.is_active = True
        user.account_activated = True
        user.save()

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, 'Successfully activated your account.')
        return redirect('/')

    messages.warning(request, 'Activation link is invalid or expired.')
    
    return render(
        request,
        'accounts/activation/activation_email_failed.html',
    )
