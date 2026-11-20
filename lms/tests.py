from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Course, Lesson, Subscription

User = get_user_model()


class LessonCRUDTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(email='owner@test.com', password='TestPass123')
        self.moderator = User.objects.create_user(email='mod@test.com', password='TestPass123')
        mod_group, _ = Group.objects.get_or_create(name='moderators')
        self.moderator.groups.add(mod_group)
        self.other = User.objects.create_user(email='other@test.com', password='TestPass123')
        self.course = Course.objects.create(title='Курс', owner=self.owner)
        self.lesson = Lesson.objects.create(
            title='Урок', course=self.course, owner=self.owner,
            video_url='https://youtube.com/watch?v=abc'
        )

    def test_create_lesson_owner(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/lessons/', {
            'title': 'Новый урок', 'course': self.course.id,
            'video_url': 'https://youtube.com/watch?v=xyz'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lesson_moderator_forbidden(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.post('/api/lessons/', {
            'title': 'Урок модератора', 'course': self.course.id
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_lesson_bad_url(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/lessons/', {
            'title': 'Урок', 'course': self.course.id,
            'video_url': 'https://rutube.ru/video/1'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_lesson_owner(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_lesson_other_forbidden(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.get(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_lesson_moderator(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.put(f'/api/lessons/{self.lesson.id}/', {
            'title': 'Обновлено', 'course': self.course.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_lesson_moderator_forbidden(self):
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_owner(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class SubscriptionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='sub@test.com', password='TestPass123')
        self.course = Course.objects.create(title='Курс', owner=self.user)

    def test_subscribe(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/subscribe/', {'course': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка добавлена')
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe(self):
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/subscribe/', {'course': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка удалена')
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscribe_no_course_error(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/subscribe/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscribe_unauthenticated(self):
        response = self.client.post('/api/subscribe/', {'course': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
