from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    StoryViewSet,
    CollectionViewSet
)


router = DefaultRouter()

router.register(r'stories', StoryViewSet, basename='story')
router.register(
    r'users/(?P<username>[^/.]+)/collections', CollectionViewSet, basename='collection'
)


urlpatterns = [
    path('', include(router.urls))
]
