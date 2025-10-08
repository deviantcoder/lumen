from django.urls import path

from . import views


app_name = 'stories'


urlpatterns = [
    path('', views.stories, name='stories'),
    path('create/', views.create_story, name='create_story'),
]
