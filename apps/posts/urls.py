from django.urls import path

from . import views


app_name = 'posts'


urlpatterns = [
    path('', views.feed, name='feed'),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('posts/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('posts/<int:post_id>/save/', views.toggle_save, name='toggle_save'),
    path('posts/<int:post_id>/preview/', views.post_preview, name='post_preview'),
    path('posts/<int:post_id>/add-comment/', views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/reply-form/<int:comment_id>/', views.reply_form, name='reply_form'),
    path('posts/<int:post_id>/share/', views.share_post, name='share_post'),
    path('posts/<int:post_id>/share/chat/', views.send_post_to_chat, name='send_post_to_chat'),
    path('posts/<int:parent_id>/replies/', views.load_replies, name='load_replies'),
]
