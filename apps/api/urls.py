from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView
)


urlpatterns = [
    path('', include('apps.api.auth.urls')),
    path('', include('apps.api.profiles.urls')),
    path('', include('apps.api.posts.urls')),
    path('', include('apps.api.stories.urls')),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
