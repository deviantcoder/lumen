from rest_framework import serializers

from apps.stories.models import Story


class StorySerializer(serializers.ModelSerializer):

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
