from rest_framework import viewsets, generics, permissions
from rest_framework.permissions import IsAuthenticated, BasePermission
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='moderators').exists()


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user




class IsModeratorOrOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        is_moderator = request.user.groups.filter(name='moderators').exists()
        is_owner = obj.owner == request.user
        return is_moderator or is_owner


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), IsOwner()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsModeratorOrOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsOwner()]
        elif self.request.method in ['PUT', 'PATCH']:
            return [IsAuthenticated(), IsModeratorOrOwner()]
        return [IsAuthenticated()]
