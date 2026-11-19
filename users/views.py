from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import User, Payment
from .serializers import UserSerializer, PaymentSerializer, RegisterSerializer
from .filters import PaymentFilter
from .services import create_stripe_product, create_stripe_price, create_stripe_session, get_stripe_session
from django.shortcuts import get_object_or_404
from lms.models import Course


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'message': 'Пользователь успешно создан', 'user_id': user.id},
            status=status.HTTP_201_CREATED
        )


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date']


class PaymentCreateView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_id = request.data.get('course')
        amount = request.data.get('amount')
        if not course_id or not amount:
            return Response({'detail': 'Укажите course и amount'}, status=400)

        course = get_object_or_404(Course, id=course_id)
        payment = Payment.objects.create(
            user=request.user, course=course, amount=amount, payment_method='stripe'
        )

        product = create_stripe_product(course.title, course.description)
        price = create_stripe_price(product.id, payment.amount)
        session = create_stripe_session(
            price.id,
            'http://127.0.0.1:8000/api/payments/success/',
            'http://127.0.0.1:8000/api/payments/cancel/',
        )

        payment.stripe_product_id = product.id
        payment.stripe_price_id = price.id
        payment.stripe_session_id = session.id
        payment.payment_url = session.url
        payment.save()

        return Response({
            'payment_id': payment.id,
            'payment_url': payment.payment_url,
            'stripe_product_id': payment.stripe_product_id,
            'stripe_price_id': payment.stripe_price_id,
            'stripe_session_id': payment.stripe_session_id,
        }, status=201)


class PaymentStatusView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        payment = get_object_or_404(Payment, id=pk, user=request.user)
        if not payment.stripe_session_id:
            return Response({'detail': 'Платёж не связан со Stripe'}, status=400)

        session = get_stripe_session(payment.stripe_session_id)
        payment.is_paid = session.payment_status == 'paid'
        payment.save()

        return Response({
            'payment_id': payment.id,
            'status': session.payment_status,
            'is_paid': payment.is_paid,
        })
