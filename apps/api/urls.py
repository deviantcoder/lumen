from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView
)

from apps.api.auth import views as auth_views


app_name = 'api'


urlpatterns = [
    path('register/', auth_views.RegisterAPIView.as_view(), name='register'),
    path('me/', auth_views.CurrentUserAPIView.as_view(), name='current_user'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
