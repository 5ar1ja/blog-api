from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_welcome_email(user_email, first_name):
    subject = 'Welcome to Blog API!'
    message = f'Hi {first_name},\n\nThank you for registering at Blog API. We are glad to have you on board.'
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@blogapi.local')
    
    send_mail(
        subject,
        message,
        from_email,
        [user_email],
        fail_silently=True,
    )
    return f'Welcome email sent to {user_email}'
