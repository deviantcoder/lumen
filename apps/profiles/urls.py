from django.urls import path

from . import views


app_name = 'profiles'


urlpatterns = [
    path('edit/', views.edit_profile, name='edit_profile'),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/posts/', views.get_user_posts, name='get_user_posts'),
]
