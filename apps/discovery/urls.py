from django.urls import path, include


app_name = 'discovery'


urlpatterns = [
    path('explore/', include('apps.discovery.explore.urls')),
    path('search/', include('apps.discovery.search.urls')),
]
