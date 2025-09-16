from django.contrib import admin

from .models import Post, PostMedia, Tag, Like


class PostMediaInline(admin.StackedInline):
    model = PostMedia
    extra = 1
    max_num = 10


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [PostMediaInline]
    list_display = (
        'author', 'caption_short', 'likes_count', 'status', 'created'
    )

    def caption_short(self, obj):
        return obj.caption[:20] + '...'
    
    def likes_count(self, obj):
        return obj.likes.count()


@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'post', 'created'
    )
