from django.contrib.auth import get_user_model

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import StorySerializer
from .permissions import IsAuthorOrReadOnly

from apps.stories.models import Story


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
