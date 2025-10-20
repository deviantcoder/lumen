from django.urls import path, include


app_name = 'api'


urlpatterns = [
    path('auth/', include('apps.api.auth.urls')),
]
