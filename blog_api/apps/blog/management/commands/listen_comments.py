import json
import redis
from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Subscribes to Redis channel "comments" and prints new messages'

    def handle(self, *args, **options):
        redis_url = getattr(settings, 'REDIS_URL', 'redis://127.0.0.1:6379/1')
        r = redis.from_url(redis_url)
        
        pubsub = r.pubsub()
        pubsub.subscribe('comments')

        self.stdout.write(self.style.SUCCESS('[*] Waiting for comments. To exit press CTRL+C'))

        try:
            for message in pubsub.listen():
                if message['type'] == 'message':
                    data = json.loads(message['data'].decode('utf-8'))
                    
                    self.stdout.write(self.style.HTTP_INFO(
                        f"\n[NEW COMMENT]\n"
                        f"Post Slug: {data['post']}\n"
                        f"Author:    {data['author']}\n"
                        f"Body:      {data['comment']}\n"
                        f"-------------------"
                    ))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nStopping listener...'))