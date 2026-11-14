from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='moderators').exists()


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsModeratorOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        is_moderator = request.user.is_authenticated and request.user.groups.filter(name='moderators').exists()
        is_owner = obj.owner == request.user
        return is_moderator or is_owner
