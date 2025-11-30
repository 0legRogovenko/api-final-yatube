from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)

from posts.models import Group, Post

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
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['group']

    def perform_create(self, serializer):
        """Сохраняет автора поста как текущего пользователя."""

        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с комментариями конкретного поста."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_post(self):
        """Возвращает ID поста из URL."""

        return get_object_or_404(Post, id=self.kwargs['post_id'])

    def get_queryset(self):
        """Возвращает queryset комментариев для конкретного поста."""

        return self.get_post().comments.all()

    def perform_create(self, serializer):
        """Сохраняет автора и привязывает комментарий к посту."""

        serializer.save(
            author=self.request.user,
            post=self.get_post(),
        )


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """ReadOnly ViewSet для групп."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


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

    def get_queryset(self):
        """Возвращает подписки текущего пользователя."""

        return self.request.user.followers.all()

    def perform_create(self, serializer):
        """При создании подписки сохраняет user текущего пользователя."""

        serializer.save(user=self.request.user)
