from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.exceptions import NotAuthenticated
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle

from posts.models import Comment, Follow, Group, Post

from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CommentSerializer,
    FollowSerializer,
    GroupSerializer,
    PostSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD операций с постами."""

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['group']
    throttle_scope = 'posts'
    throttle_classes = [ScopedRateThrottle]

    def perform_create(self, serializer):
        """Сохраняет автора поста как текущего пользователя."""

        if not self.request.user.is_authenticated:
            raise NotAuthenticated(
                'Только аутентифицированные пользователи могут '
                'создавать посты.'
            )

        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с комментариями конкретного поста."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]
    throttle_scope = 'comments'
    throttle_classes = [ScopedRateThrottle]

    def get_queryset(self):
        """Возвращает queryset комментариев для конкретного поста."""

        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post__id=post_id)

    def perform_create(self, serializer):
        """Сохраняет автора и привязывает комментарий к посту."""

        if not self.request.user.is_authenticated:
            raise NotAuthenticated(
                'Только аутентифицированные пользователи могут '
                'создавать комментарии.'
            )

        post_id = self.kwargs.get('post_id')
        serializer.save(
            author=self.request.user,
            post=get_object_or_404(Post, id=post_id),
        )


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """ReadOnly ViewSet для групп."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    throttle_scope = 'groups'
    throttle_classes = [ScopedRateThrottle]


class FollowViewSet(
    ListModelMixin,
    CreateModelMixin,
    viewsets.GenericViewSet
):
    """ViewSet для управления подписками пользователя."""

    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['following__username']
    throttle_scope = 'follows'
    throttle_classes = [ScopedRateThrottle]

    def get_queryset(self):
        """Возвращает подписки текущего пользователя."""

        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """При создании подписки сохраняет user текущего пользователя."""

        serializer.save(user=self.request.user)
