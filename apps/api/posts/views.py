from django.db.models import Count, Exists, OuterRef

from rest_framework.generics import RetrieveAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import (
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer
)
from .permissions import IsAuthorOrReadOnly

from apps.posts.models import Post, Like, Save


class PostViewSet(ModelViewSet):

    serializer_class = PostSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        
        if self.action == 'retrieve':
            return PostDetailSerializer
        
        return PostSerializer

    def get_queryset(self):
        queryset = (
            Post.objects.select_related(
                'author', 'author__profile'
            )
            .prefetch_related(
                'media', 'tags', 'likes', 'comments'
            )
            .annotate(
                likes_count=Count('likes', distinct=True),
                comments_count=Count('comments', distinct=True),
                liked_by_user=Exists(
                    Like.objects.filter(
                        user=self.request.user, post=OuterRef('pk')
                    )
                ),
                saved_by_user=Exists(
                    Save.objects.filter(
                        user=self.request.user, post=OuterRef('pk')
                    )
                )
            )
        )

        author_username = self.request.query_params.get('author_username', '')
        caption = self.request.query_params.get('caption', '')

        if author_username:
            queryset = queryset.filter(author__username__icontains=author_username)

        if caption:
            queryset = queryset.filter(caption__icontains=caption)

        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
