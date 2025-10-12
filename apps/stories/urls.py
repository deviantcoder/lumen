from django.urls import path

from . import views


app_name = 'stories'


urlpatterns = [
    path('create/', views.create_story, name='create_story'),
    path('stories-list/', views.stories_list, name='stories_list'),
    path('<str:username>/', views.stories, name='stories'),
    path('<str:username>/<int:story_id>/', views.stories, name='stories_with_id'),
    path('<int:story_id>/share/', views.share_story, name='share_story'),
    path('<int:story_id>/share/chat/', views.send_story_to_chat, name='send_story_to_chat'),
]
