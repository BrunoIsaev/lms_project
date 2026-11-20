from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsOwner, IsModeratorOrOwner, IsNotModerator
from .paginators import CourseLessonPagination
from .tasks import send_course_update_notification


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    pagination_class = CourseLessonPagination
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

    def perform_update(self, serializer):
        serializer.save()
        send_course_update_notification.delay(self.get_object().id)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    pagination_class = CourseLessonPagination
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

    def perform_update(self, serializer):
        serializer.save()
        course = self.get_object().course
        send_course_update_notification.delay(course.id)

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


class SubscriptionView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course')
        if not course_id:
            return Response({'detail': 'Не указан course_id'}, status=400)

        course = get_object_or_404(Course, id=course_id)
        sub = Subscription.objects.filter(user=user, course=course)

        if sub.exists():
            sub.delete()
            message = 'подписка удалена'
        else:
            Subscription.objects.create(user=user, course=course)
            message = 'подписка добавлена'

        return Response({'message': message})
