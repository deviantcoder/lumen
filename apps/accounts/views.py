from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import generic

from .forms import LoginForm, SignupForm


class LoginUserView(LoginView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)

        user = self.request.user

        if user.email_verified:
            messages.success(self.request, 'Welcome back!')
            return redirect(self.get_success_url())
        else:
            messages.warning(self.request, 'Please verify your email before logging in.')
            logout(self.request)
            return redirect('home')
    
    def form_invalid(self, form):
        messages.warning(self.request, 'Invalid email, username or password.')
        return super().form_invalid(form)


class LogoutUserView(LogoutView):
    pass


class SignupUserView(generic.CreateView):
    template_name = 'accounts/signup.html'
    form_class = SignupForm
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')

        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)

        user = form.instance

        if user is not None:
            # send verification email
            return redirect('/')
        
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.warning(self.request, f'{field.capitalize()}: {error}.')
        return super().form_invalid(form)
