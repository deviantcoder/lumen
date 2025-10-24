from rest_framework import serializers

from apps.profiles.models import Profile, Follow


class ProfileSerializer(serializers.ModelSerializer):

    username = serializers.ReadOnlyField(source='user.username')
    full_name = serializers.ReadOnlyField(source='user.full_name')

    email = serializers.CharField(source='user.email', read_only=True)

    image = serializers.SerializerMethodField()

    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Profile
        fields = (
            'id',
            'username',
            'full_name',
            'email',
            'image',
            'followers_count',
            'following_count',
            'bio',
            'location',
            'url',
            'created'
        )

    def get_image(self, obj):
        return obj.image_or_default


class ProfileListSerializer(ProfileSerializer):

    profile_url = serializers.HyperlinkedIdentityField(
        view_name='profile-detail',
        lookup_field='pk'
    )

    followed_by_me = serializers.BooleanField(read_only=True)

    class Meta:
        model = Profile
        fields = (
            'profile_url', 'url', 'id', 'username', 'full_name', 'image', 'followed_by_me'
        )
