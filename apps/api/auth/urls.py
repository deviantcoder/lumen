from django.urls import path

from . import views


urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('me/', views.CurrentUserAPIView.as_view(), name='current_user'),
]
