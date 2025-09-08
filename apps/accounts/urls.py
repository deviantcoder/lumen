from django.urls import path

from . import views


app_name = 'accounts'


urlpatterns = [
    path('signin/', views.LoginUserView.as_view(), name='login'),
    path('logout/', views.LogoutUserView.as_view(), name='logout'),
    path('signup/', views.SignupUserView.as_view(), name='signup'),

    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),
]
