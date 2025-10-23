from django.db.models import Count

from rest_framework.generics import (
    get_object_or_404,
    RetrieveAPIView,
    ListAPIView
)
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin

from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import (
    ProfileSerializer,
    ProfileListSerializer
)

from apps.profiles.models import Profile


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


class ProfileListAPIView(ListAPIView):
    serializer_class = ProfileListSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

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
                following_count=Count('user__following', distinct=True)
            )
        )

        return queryset


class ProfileDetailAPIView(RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
