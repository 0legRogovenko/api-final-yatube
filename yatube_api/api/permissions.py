from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Только автор может редактировать, остальные — только чтение."""

    def has_object_permission(self, request, view, obj):
        """Проверяет права: безопасные методы доступны всем, иные — автору."""

        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
