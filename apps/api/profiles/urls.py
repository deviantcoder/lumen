from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    CurrentUserProfileAPIView,
    ProfileViewSet,
    ProfileFollowersAPIView,
    ProfileFollowingAPIView
)


router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')


urlpatterns = [
    path('profiles/me/', CurrentUserProfileAPIView.as_view(), name='current-profile'),

    path('profiles/<str:username>/followers/', ProfileFollowersAPIView.as_view(), name='profile-followers'),
    path('profiles/<str:username>/following/', ProfileFollowingAPIView.as_view(), name='profile-following'),

    path('', include(router.urls)),
]
