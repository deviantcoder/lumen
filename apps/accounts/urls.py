from django.urls import path

from . import views


app_name = 'accounts'


urlpatterns = [
    # path('signin/', views.login_view, name='login'),
    path('signin/', views.LoginUserView.as_view(), name='login'),
]
