from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Разрешение только для владельца объекта."""
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsModerator(BasePermission):
    """Разрешение только для модератора."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='moderators').exists()


class IsModeratorOrOwner(BasePermission):
    """Разрешение для модератора ИЛИ владельца объекта."""
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        is_moderator = request.user.groups.filter(name='moderators').exists()
        is_owner = obj.owner == request.user
        return is_moderator or is_owner


class IsNotModerator(BasePermission):
    """Запрет для модератора (используется при создании объектов)."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return not request.user.groups.filter(name='moderators').exists()
