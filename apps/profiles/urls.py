from django.urls import path

from . import views


app_name = 'profiles'


urlpatterns = [
    path('edit/', views.edit_profile, name='edit_profile'),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/posts/', views.get_user_posts, name='get_user_posts'),
    path('update/url/', views.update_profile_url, name='update_profile_url'),
    path('update/bio/', views.update_profile_bio, name='update_profile_bio'),
    path('update/image/', views.update_profile_image, name='update_profile_image'),
    path('<str:username>/follow/', views.toggle_follow, name='toggle_follow'),
]
