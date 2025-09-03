from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.contrib import messages

from .forms import LoginForm


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
