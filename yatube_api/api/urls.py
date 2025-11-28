from django.urls import include, path

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    CommentViewSet,
    FollowViewSet,
    GroupViewSet,
    PostViewSet,
)

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='posts')
router.register(r'groups', GroupViewSet, basename='groups')
router.register(r'follow', FollowViewSet, basename='follows')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'posts/<int:post_id>/comments/',
        CommentViewSet.as_view({
            'get': 'list',
            'post': 'create',
        }),
        name='comments',
    ),
    path(
        'posts/<int:post_id>/comments/<int:pk>/',
        CommentViewSet.as_view({
            'delete': 'destroy',
            'get': 'retrieve',
            'patch': 'partial_update',
            'put': 'update',
        }),
        name='comment-detail',
    ),
    path(
        'jwt/create/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair',
    ),
    path(
        'jwt/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh',
    ),
    path(
        'jwt/verify/',
        TokenVerifyView.as_view(),
        name='token_verify',
    ),
]
