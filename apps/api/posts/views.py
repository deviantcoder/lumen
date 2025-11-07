from django.db.models import (
    Count, Exists, OuterRef, Q, F, Case, When, IntegerField
)
from django.utils import timezone

from datetime import timedelta

from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import (
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostMediaSerializer
)
from .permissions import IsAuthorOrReadOnly

from apps.posts.models import Post, Like, Save


class PostViewSet(ModelViewSet):

    serializer_class = PostSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    http_method_names = ['get', 'patch', 'post', 'delete']

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

    @action(
        methods=['POST'],
        detail=True,
        url_path='upload-media'
    )
    def upload_media(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)

        files = request.FILES.getlist('media')
        
        if not files:
            return Response(
                {'detail': 'No media files provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = [{'file': file} for file in files]

        serializer = PostMediaSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(
        methods=['POST'],
        detail=True,
        url_name='like'
    )
    def like(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)

        if Like.objects.filter(
            user=self.request.user, post=post
        ).exists():
            return Response(
                {'detail': 'You have already liked this post.'},
                status=status.HTTP_409_CONFLICT
            )
        
        Like.objects.create(user=self.request.user, post=post)

        return Response(
            {'detail': 'You liked this post.'},
            status=status.HTTP_201_CREATED
        )
    
    @action(
        methods=['POST'],
        detail=True,
        url_name='unlike'
    )
    def unlike(self, request, pk=None):
        post = get_object_or_404(Post, pk=pk)

        try:
            like = Like.objects.get(
                user=self.request.user, post=post
            )

            like.delete()

            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        except Like.DoesNotExist:
            return Response(
                {'detail': 'You have not liked this post.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(
        methods=["GET"],
        detail=False,
        url_path="my-posts"
    )
    def my_posts(self, request):
        user = request.user

        queryset = self.get_queryset().filter(author=user)
        serializer = PostListSerializer(queryset, many=True)

        return Response(serializer.data)
    
    @action(
        methods=['GET'],
        detail=False,
        url_name='liked'
    )
    def liked(self, request):
        user = request.user

        queryset = self.get_queryset().filter(likes__user=user)
        serializer = PostListSerializer(queryset, many=True)

        return Response(serializer.data)
    
    @action(
        methods=['GET'],
        detail=False,
        url_name='saved'
    )
    def saved(self, request):
        user = request.user

        queryset = self.get_queryset().filter(saves__user=user)
        serializer = PostListSerializer(queryset, many=True)

        return Response(serializer.data)

    @action(
        methods=['GET'],
        detail=False,
        url_name='feed'
    )
    def feed(self, request):
        user = request.user

        queryset = (
            self.get_queryset().filter(
                Q(author=user) | Q(author__followers__follower=user)
            )
            .annotate(
                priority_score=Case(
                    When(author=user, then=100),
                    default=10,
                    output_field=IntegerField()
                ),
                time_score=Case(
                    When(created__gte=timezone.now() - timedelta(hours=24), then=20),
                    When(created__gte=timezone.now() - timedelta(days=7), then=10),
                    When(created__gte=timezone.now() - timedelta(days=30), then=5),
                    default=1,
                    output_field=IntegerField()
                ),
            )
            .annotate(
                final_score=(
                    F("priority_score") + F("time_score") + F("likes_count") + F("comments_count")
                )
            )
            .order_by(
                '-final_score', '-created'
            )
        )

        serializer = PostListSerializer(queryset, many=True)

        return Response(serializer.data)
