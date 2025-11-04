from rest_framework import serializers

from apps.posts.models import Post


class PostSerializer(serializers.ModelSerializer):

    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Post
        fields = (
            'id',
            'author',
            'caption',
            'tags',
            'likes_count',
            'comments_count',
            'created',
        )
