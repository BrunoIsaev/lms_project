from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsOwner, IsModeratorOrOwner, IsNotModerator


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action == 'create':
            # Модератор НЕ может создавать курсы
            return [IsAuthenticated(), IsNotModerator()]
        elif self.action == 'retrieve':
            # Детальный просмотр только для владельца
            return [IsAuthenticated(), IsOwner()]
        elif self.action in ['update', 'partial_update']:
            # Редактировать может модератор ИЛИ владелец
            return [IsAuthenticated(), IsModeratorOrOwner()]
        elif self.action == 'destroy':
            # Удалять может только владелец
            return [IsAuthenticated(), IsOwner()]
        # Список курсов — любой авторизованный
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            # Модератор НЕ может создавать уроки
            return [IsAuthenticated(), IsNotModerator()]
        # Список уроков — любой авторизованный
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            # Удалять может только владелец
            return [IsAuthenticated(), IsOwner()]
        elif self.request.method in ['PUT', 'PATCH']:
            # Редактировать может модератор ИЛИ владелец
            return [IsAuthenticated(), IsModeratorOrOwner()]
        elif self.request.method == 'GET':
            # Детальный просмотр только для владельца
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]
