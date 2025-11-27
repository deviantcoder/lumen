from django.urls import path

from . import views


app_name = 'profiles'


urlpatterns = [
    path('edit/', views.edit_profile, name='edit_profile'),
    path('suggestions/', views.suggestions_list, name='suggestions_list'),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/posts/', views.get_user_posts, name='get_user_posts'),
    path('<str:username>/follow/', views.toggle_follow, name='toggle_follow'),
    path('<str:username>/followers/', views.get_followers, name='get_followers'),
    path('<str:username>/following/', views.get_following, name='get_following'),
]
