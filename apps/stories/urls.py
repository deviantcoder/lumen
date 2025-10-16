from django.urls import path

from . import views


app_name = 'stories'


urlpatterns = [
    # stories
    path('create/', views.create_story, name='create_story'),
    path('stories-list/', views.stories_list, name='stories_list'),
    path('<str:username>/', views.stories, name='stories'),
    path('<str:username>/<int:story_id>/', views.stories, name='stories_with_id'),
    path('<int:story_id>/share/', views.share_story, name='share_story'),
    path('<int:story_id>/share/chat/', views.send_story_to_chat, name='send_story_to_chat'),
    path('<int:story_id>/reply/', views.send_story_reply, name='send_story_reply'),
    path('<int:story_id>/delete/', views.delete_story, name='delete_story'),

    path('<int:story_id>/save/', views.save_story_to_collection, name='save_story_to_collection'),

    # collections
    path('collections/create/', views.create_collection, name='create_collection'),
    path('collections/<str:username>/', views.collections_list, name='collections_list'),
    path('collections/view/<str:collection_uid>/', views.collection, name='collection'),
    path(
        'collections/view/<str:collection_uid>/<int:story_id>/',
        views.collection,
        name='collection_story_with_id'
    ),
    path(
        'collections/<str:collection_uid>/remove/<int:story_id>/',
        views.remove_story_from_collection,
        name='remove_story_from_collection'
    ),
    path('collections/edit/<int:collection_id>/', views.edit_collection, name='edit_collection'),
]
