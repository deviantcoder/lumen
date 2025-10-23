from django.urls import path

from .views import (
    ProfileListAPIView,
    ProfileDetailAPIView,
    CurrentUserProfileAPIView
)


urlpatterns = [
    path('', ProfileListAPIView.as_view(), name='profile-list'),
    path('<int:pk>/', ProfileDetailAPIView.as_view(), name='profile-detail'),
    path('me/', CurrentUserProfileAPIView.as_view(), name='current-profile'),
]
