from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
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


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'phone', 'city')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует')
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'
