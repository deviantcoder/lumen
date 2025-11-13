from rest_framework import serializers

from apps.profiles.models import Profile, Follow


class ProfileSerializer(serializers.ModelSerializer):

    """
    Serializer for user profiles.
    """

    username = serializers.ReadOnlyField(source='user.username')
    full_name = serializers.ReadOnlyField(source='user.full_name')

    email = serializers.CharField(source='user.email', read_only=True)

    image = serializers.ImageField(required=False, allow_null=True)

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


class ProfileListSerializer(ProfileSerializer):

    """
    Serializer for listing user profiles.
    """

    profile_url = serializers.HyperlinkedIdentityField(
        view_name='profile-detail',
        lookup_field='username'
    )

    followed_by_me = serializers.BooleanField(read_only=True)

    class Meta:
        model = Profile
        fields = (
            'id',
            'profile_url',
            'url',
            'username',
            'full_name',
            'image',
            'followed_by_me',
        )


class FollowerSerializer(serializers.ModelSerializer):

    """
    Serializer for profile followers.
    """
    
    profile_id = serializers.IntegerField(
        source='follower.profile.pk', read_only=True
    )
    username = serializers.CharField(
        source='follower.username', read_only=True
    )
    profile_url = serializers.HyperlinkedRelatedField(
        source='follower.profile',
        view_name='profile-detail',
        lookup_field='username',
        read_only=True
    )

    class Meta:
        model = Follow
        fields = (
            'profile_id', 'username', 'profile_url'
        )


class FollowingSerializer(serializers.ModelSerializer):

    """
    Serializer for profiles being followed.
    """

    profile_id = serializers.IntegerField(
        source='user.profile.pk', read_only=True
    )
    username = serializers.CharField(
        source='user.username', read_only=True
    )
    profile_url = serializers.HyperlinkedRelatedField(
        source='user.profile',
        view_name='profile-detail',
        lookup_field='username',
        read_only=True
    )

    class Meta:
        model = Follow
        fields = (
            'profile_id', 'username', 'profile_url'
        )
