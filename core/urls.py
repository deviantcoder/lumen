from django.contrib import admin
from django.urls import path, include

from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/', include('apps.accounts.urls')),
    path('accounts/social/', include('social_django.urls', namespace='social')),

    path('posts/', include('apps.posts.urls')),
    path('profiles/', include('apps.profiles.urls')),

    path('', include('apps.feed.urls')),

    # password reset
    path(
        'reset_password/',
        auth_views.PasswordResetView.as_view(template_name='accounts/password_reset/reset_password.html'),
        name='reset_password'
    ),
    path(
        'reset_password_sent/',
        auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path(
        'reset_password_complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset/password_reset_complete.html'),
        name='password_reset_complete'
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
