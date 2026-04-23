import logging
import redis
import json

from django.core.cache import cache
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.conf import settings

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import StreamingHttpResponse

from .models import Post
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly

logger = logging.getLogger(__name__)
redis_client = redis.from_url(settings.CACHES['default']['LOCATION']) 

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'slug'
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        if self.action == 'list':
            return Post.objects.filter(status='published')
        return super().get_queryset()

    # Лимит для POST /api/posts/ — 20/мин на пользователя (Пункт 13.2 ТЗ)
    @method_decorator(ratelimit(key='user', rate='20/m', method='POST', block=True))
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        from .tasks import invalidate_post_cache
        serializer.save(author=self.request.user)
        invalidate_post_cache.delay()
        logger.info('Post created by %s', self.request.user.email)

    def perform_update(self, serializer):
        from .tasks import invalidate_post_cache
        serializer.save()
        invalidate_post_cache.delay()

    def perform_destroy(self, instance):
        from .tasks import invalidate_post_cache
        logger.info('Post deleted: %s', instance.slug)
        instance.delete()
        invalidate_post_cache.delay()

    def list(self, request, *args, **kwargs):
        cache_key = "posts_list_cache"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        
        cache.set(cache_key, response.data, 60)
        return response

    @action(detail=True, methods=['get', 'post'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def comments(self, request, slug=None):
        post = self.get_object()

        if request.method == 'GET':
            comments = post.comments.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        if request.method == 'POST':
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                comment = serializer.save(author=request.user, post=post)
                
                message = json.dumps({
                    "post": post.slug, 
                    "author": comment.author.email,
                    "comment": comment.body
                })
                redis_client.publish('comments', message)
                
                logger.info('Comment added to post %s by %s', post.slug, request.user.email)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class PostStreamView(APIView):
    permission_classes = [permissions.AllowAny]

    async def get(self, request):
        async def event_stream():
            import redis.asyncio as redis_async
            from django.conf import settings
            import asyncio
            
            r = redis_async.from_url(settings.REDIS_URL)
            pubsub = r.pubsub()
            await pubsub.subscribe("live_posts")
            
            try:
                # Keep connection alive with ping or wait for messages
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        data = message["data"].decode("utf-8")
                        yield f"data: {data}\n\n"
            finally:
                await pubsub.unsubscribe("live_posts")
                await pubsub.close()

        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
