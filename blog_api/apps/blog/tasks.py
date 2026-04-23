from celery import shared_task
from django.core.cache import cache
from .models import Post

@shared_task
def invalidate_post_cache():
    cache.delete("posts_list_cache")
    return "Post cache invalidated"

@shared_task
def publish_scheduled_posts():
    # Example task that publishes posts if you had a scheduled_time field
    # For now, it just demonstrates a periodic task.
    # In a real app: Post.objects.filter(status='draft', scheduled_publish_date__lte=timezone.now()).update(status='published')
    return "Checked for scheduled posts"
