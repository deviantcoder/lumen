from rest_framework import serializers

from apps.stories.models import Story, Collection


class StorySerializer(serializers.ModelSerializer):

    """
    Serializer for stories.
    """

    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Story
        fields = (
            'id',
            'author',
            'media',
            'created',
            'expires_at'
        )


class CollectionSerializer(serializers.ModelSerializer):

    """
    Serializer for story collections.
    """

    author = serializers.ReadOnlyField(source='author.username')
    stories = StorySerializer(many=True, read_only=True)

    class Meta:
        model = Collection
        fields = (
            'id',
            'author',
            'name',
            'image',
            'stories',
            'created'
        )
