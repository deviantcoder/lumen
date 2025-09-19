from django.urls import path

from . import views


app_name = 'profiles'


urlpatterns = [
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/posts/', views.get_user_posts, name='get_user_posts'),
]
