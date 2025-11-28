from django.urls import path

from . import views


urlpatterns = [
    path('auth/register/', views.RegisterAPIView.as_view(), name='register'),
    path('auth/me/', views.CurrentUserAPIView.as_view(), name='current_user'),
]
