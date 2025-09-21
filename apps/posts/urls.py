from django.urls import path

from . import views


app_name = 'posts'


urlpatterns = [
    path('create/', views.create_post, name='create_post'),
    path('<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('<int:post_id>/save/', views.toggle_save, name='toggle_save'),
    path('<int:post_id>/preview/', views.post_preview, name='post_preview'),
    path('<int:post_id>/add-comment/', views.add_comment, name='add_comment'),
]
