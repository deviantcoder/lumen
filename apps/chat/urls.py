from django.urls import path

from . import views


app_name = 'chat'


urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('chat/<str:chat_id>/', views.chat, name='chat'),
    path('chat/start/<str:username>/', views.start_chat, name='start_chat'),
]
