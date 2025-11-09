from django.contrib import admin

from .models import Story, Collection


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = (
        'author', 'media_type', 'expires_at'
    )


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = (
        'author', 'name'
    )
