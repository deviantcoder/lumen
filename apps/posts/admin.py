from django.contrib import admin

from .models import Post, PostMedia, Tag


class PostMediaInline(admin.StackedInline):
    model = PostMedia
    extra = 1
    max_num = 10


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [PostMediaInline]


@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}
