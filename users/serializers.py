from rest_framework import serializers
from .models import User, Payment
from lms.models import Course, Lesson


class CourseMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'title')


class LessonMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'title')


class PaymentSerializer(serializers.ModelSerializer):
    course = CourseMiniSerializer(read_only=True)
    lesson = LessonMiniSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'payment_date', 'course', 'lesson', 'amount', 'payment_method')


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'payments')
