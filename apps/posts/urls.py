from django.urls import path

from . import views


app_name = 'posts'


urlpatterns = [
    path('create/', views.create_post, name='create_post'),
    path('<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('<int:post_id>/save/', views.toggle_save, name='toggle_save'),
    path('<int:post_id>/preview/', views.post_preview, name='post_preview'),
    path('<int:post_id>/add-comment/', views.add_comment, name='add_comment'),
    path('<int:post_id>/reply-form/<int:comment_id>/', views.reply_form, name='reply_form'),
    path('<int:post_id>/share/', views.share_post, name='share_post'),
    path('<int:post_id>/share/chat/', views.send_post_to_chat, name='send_post_to_chat'),
    path('<int:parent_id>/replies/', views.load_replies, name='load_replies'),
]
