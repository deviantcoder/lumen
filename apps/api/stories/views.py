from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import StorySerializer
from .permissions import IsAuthorOrReadOnly

from apps.stories.models import Story


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
