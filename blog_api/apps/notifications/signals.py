from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.blog.models import Comment, Post
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

@receiver(post_save, sender=Comment)
def comment_created(sender, instance, created, **kwargs):
    if created:
        # Create notification for post author
        post_author = instance.post.author
        if post_author != instance.author:
            Notification.objects.create(
                user=post_author,
                message=f"New comment on your post '{instance.post.title}' by {instance.author.get_full_name() or instance.author.email}"
            )
        
        # Broadcast via WebSockets
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"post_{instance.post.id}_comments",
            {
                "type": "chat_message",
                "message": {
                    "id": instance.id,
                    "author": instance.author.get_full_name() or instance.author.email,
                    "body": instance.body,
                    "created_at": instance.created_at.isoformat(),
                }
            }
        )

@receiver(post_save, sender=Post)
def post_status_changed(sender, instance, **kwargs):
    # This is for SSE, we will push an event to a Redis channel
    if instance.status == 'published':
        import json
        import redis
        from django.conf import settings
        r = redis.from_url(settings.REDIS_URL)
        message = {
            "id": instance.id,
            "title": instance.title,
            "author": instance.author.get_full_name() or instance.author.email,
        }
        r.publish("live_posts", json.dumps(message))
