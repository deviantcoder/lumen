from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import (
    StorySerializer,
    CollectionSerializer
)
from .permissions import IsAuthorOrReadOnly

from apps.stories.models import Story, Collection


User = get_user_model()


class StoryViewSet(ModelViewSet):
    
    serializer_class = StorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):

        user = self.request.user
        following_pks = list(user.following.values_list('user__pk', flat=True))
        following_pks.append(user.pk)

        queryset = (
            Story.objects.select_related(
                'author__profile'
            )
            .filter(
                author__pk__in=following_pks,
                story_type=Story.STORY_TYPES.ACTIVE
            )
            .order_by(
                'created'
            )
        )

        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['GET'],
        detail=False,
        url_path='my-stories'
    )
    def my_stories(self, request):
        user = request.user

        print(user)

        queryset = self.get_queryset().filter(author=user)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)
    
    @action(
        methods=['GET'],
        detail=False,
        url_path='(?P<username>[^/.]+)'
    )
    def stories_by_user(self, request, username=None):
        user = get_object_or_404(User, username=username)

        queryset = self.get_queryset().filter(author=user)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class CollectionViewSet(ModelViewSet):

    serializer_class = CollectionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        queryset = (
            Collection.objects.select_related(
                'author__profile'
            )
            .prefetch_related(
                'stories'
            )
            .filter(
                author=user
            )
        )

        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['post'],
        detail=True,
        url_path='add-story'
    )
    def add_story(self, request, username=None, pk=None):
        collection = self.get_object()
        story_id = request.data.get('story_id', '')

        if not story_id:
            return Response(
                {'detail': 'Story id not provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        story = get_object_or_404(Story, pk=story_id)
        
        permission = IsAuthorOrReadOnly()
        if not permission.has_object_permission(request, self, story):
            return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if collection.stories.filter(pk=story.pk).exists():
            return Response(
                {'detail': 'Story is already in collection.'},
                status=status.HTTP_409_CONFLICT
            )

        collection.stories.add(story)

        return Response(
            {'detail': 'Story added to collection.'},
            status=status.HTTP_200_OK
        )
