from rest_framework import serializers

from apps.posts.models import Post, Tag, PostMedia


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name')


class PostMediaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PostMedia
        fields = ('id', 'file', 'created')


class PostSerializer(serializers.ModelSerializer):

    author = serializers.ReadOnlyField(source='author.username')

    media = PostMediaSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Post
        fields = (
            'id',
            'author',
            'caption',
            'media',
            'tags',
            'likes_count',
            'comments_count',
            'created',
        )


class PostListSerializer(PostSerializer):

    liked_by_user = serializers.BooleanField(read_only=True)
    saved_by_user = serializers.BooleanField(read_only=True)
    
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + (
            'liked_by_user', 'saved_by_user'
        )


class PostDetailSerializer(PostSerializer):

    liked_by_user = serializers.BooleanField(read_only=True)
    saved_by_user = serializers.BooleanField(read_only=True)
    
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + (
            'liked_by_user', 'saved_by_user'
        )
