from celery import shared_task
from django.core.mail import send_mass_mail
from django.utils import timezone
from datetime import timedelta


@shared_task
def send_course_update_notification(course_id):
    """Рассылка писем подписчикам курса.
    Отправляется только если курс не обновлялся более 4 часов."""
    from .models import Course, Subscription

    course = Course.objects.filter(id=course_id).first()
    if not course:
        return {'status': 'course_not_found'}

    now = timezone.now()
    # Дополнительное задание: не отправлять, если курс обновлялся менее 4 часов назад
    if (now - course.updated_at) < timedelta(hours=4):
        return {'status': 'skipped', 'reason': 'course updated less than 4 hours ago'}

    subs = Subscription.objects.filter(course=course).select_related('user')
    if not subs.exists():
        return {'status': 'no_subscribers'}

    emails = []
    for sub in subs:
        emails.append((
            'Обновление курса',
            f'Курс "{course.title}" был обновлён.',
            'noreply@lms.com',
            [sub.user.email],
        ))

    send_mass_mail(emails, fail_silently=True)
    return {'status': 'sent', 'count': len(emails)}


@shared_task
def block_inactive_users():
    """Блокирует пользователей, не заходивших более месяца."""
    from users.models import User

    threshold = timezone.now() - timedelta(days=30)
    users = User.objects.filter(is_active=True, last_login__lt=threshold)
    count = users.count()
    users.update(is_active=False)
    return {'blocked': count}
