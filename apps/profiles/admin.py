from django.contrib import admin

from .models import Profile, Follow


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'follower', 'created')
