from rest_framework import permissions, exceptions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    GET, HEAD, OPTIONS запросы для всех,
    POST, PUT, PATCH, DELETE только для админа.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_authenticated and request.user.admin:
            return True
        else:
            raise exceptions.MethodNotAllowed(request.method)


class IsOwnerAdminOrReadOnlyPermission(permissions.BasePermission):
    """
    GET, HEAD, OPTIONS запросы для всех,
    POST для авторизованного пользователя,
    PUT, PATCH, DELETE только для автора, модератора или админа,
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.admin)
