from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    CurrentUserProfileAPIView,
    ProfileViewSet
)


router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')


urlpatterns = [
    path('profiles/me/', CurrentUserProfileAPIView.as_view(), name='current-profile'),
    path('', include(router.urls)),
]
