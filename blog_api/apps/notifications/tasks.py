from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Notification

@shared_task
def clear_expired_notifications():
    # Example: Clear notifications older than 30 days
    expiration_date = timezone.now() - timedelta(days=30)
    deleted_count, _ = Notification.objects.filter(created_at__lte=expiration_date).delete()
    return f"Deleted {deleted_count} expired notifications"

@shared_task
def process_new_comment(comment_id):
    # This could process metrics or trigger complex background work for a comment
    return f"Processed comment {comment_id}"
