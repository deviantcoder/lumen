from django.db.models import Count, Exists, OuterRef, Q
from django.contrib.auth import get_user_model

from rest_framework.generics import (
    get_object_or_404,
    RetrieveAPIView,
    ListAPIView
)
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import (
    ProfileSerializer,
    ProfileListSerializer,
    FollowerSerialzer,
    FollowingSerializer
)

from apps.profiles.models import Profile, Follow


User = get_user_model()


class CurrentUserProfileAPIView(RetrieveAPIView):
    serializer_class = ProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Profile.objects.filter(
                user=self.request.user
            )
            .select_related('user')
            .prefetch_related(
                'user__followers', 'user__following'
            )
            .annotate(
                followers_count=Count('user__followers', distinct=True),
                following_count=Count('user__following', distinct=True)
            )
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset()
        )


class ProfileViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ProfileListSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    lookup_field = 'username'
    lookup_url_kwarg = 'username'

    def get_serializer_class(self):
        if self.action == 'list':
            return ProfileListSerializer
        if self.action == 'retrieve':
            return ProfileSerializer
        return ProfileListSerializer
    
    def get_object(self):
        queryset = self.get_queryset()
        username = self.kwargs.get(self.lookup_url_kwarg)
        return get_object_or_404(queryset, user__username=username)

    def get_queryset(self):
        queryset = (
            Profile.objects.select_related(
                'user'
            )
            .prefetch_related(
                'user__followers', 'user__following'
            )
            .annotate(
                followers_count=Count('user__followers', distinct=True),
                following_count=Count('user__following', distinct=True),

                followed_by_me=Exists(
                    Follow.objects.filter(
                        follower=self.request.user,
                        user=OuterRef('user_id')
                    )
                )
            )
        )

        username = self.request.query_params.get('username', '')
        full_name = self.request.query_params.get('full_name', '')

        if username:
            queryset = queryset.filter(user__username__icontains=username)

        if full_name:
            queryset = queryset.filter(user__full_name__icontains=full_name)

        return queryset

    @action(
        detail=True,
        methods=['POST'],
        url_path='follow',
    )
    def follow(self, request, username=None):
        follower = self.request.user
        user = get_object_or_404(User, username=username)

        if follower == user:
            return Response(
                {'detail': 'You cannot follow yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if Follow.objects.filter(
            user=user, follower=follower
        ).exists():
            return Response(
                {'detail': 'You are already following this user.'},
                status=status.HTTP_409_CONFLICT
            )
        
        follow = Follow.objects.create(
            user=user, follower=follower
        )

        return Response(
            {'detail': 'You started following this user.'},
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=['POST'],
        url_path='unfollow',
    )
    def unfollow(self, request, username=None):
        follower = self.request.user
        user = get_object_or_404(User, username=username)

        try:
            follow = Follow.objects.get(
                Q(follower=follower) & Q(user=user)
            )

            follow.delete()
            
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        except Follow.DoesNotExist:
            return Response(
                {'detail': 'You are not following this user.'},
                status=status.HTTP_404_NOT_FOUND
            )


class ProfileFollowersAPIView(ListAPIView):
    serializer_class = FollowerSerialzer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        return user.followers.all()


class ProfileFollowingAPIView(ListAPIView):
    serializer_class = FollowingSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        return user.following.all()
