from django.db.models import Count, Exists, OuterRef

from rest_framework.generics import (
    get_object_or_404,
    RetrieveAPIView
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import (
    ProfileSerializer,
    ProfileListSerializer
)

from apps.profiles.models import Profile, Follow


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

    def get_serializer_class(self):
        if self.action == 'list':
            return ProfileListSerializer
        if self.action == 'retrieve':
            return ProfileSerializer
        return ProfileListSerializer

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
                        follower=self.request.user, user=OuterRef('pk')
                    )
                )
            )
        )

        return queryset
