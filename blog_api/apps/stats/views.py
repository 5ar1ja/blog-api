from rest_framework.views import APIView
from rest_framework.response import Response
import httpx
import asyncio
from asgiref.sync import sync_to_async
from apps.blog.models import Post, Comment
from apps.users.models import User

class StatsAPIView(APIView):
    """
    Why async: This view makes multiple HTTP requests to external APIs. 
    By using async (asyncio.gather), we can run these IO-bound requests concurrently,
    meaning the total wait time is bounded by the slowest request rather than the sum 
    of all request times. If written synchronously, the server would block the worker 
    thread during each request, increasing latency and reducing throughput.
    """
    async def get(self, request, *args, **kwargs):
        async with httpx.AsyncClient() as client:
            exchange_task = client.get('https://open.er-api.com/v6/latest/USD')
            time_task = client.get('https://timeapi.io/api/time/current/zone?timeZone=Asia/Almaty')
            
            # Run concurrently
            exchange_response, time_response = await asyncio.gather(exchange_task, time_task)
            
            exchange_data = exchange_response.json()
            time_data = time_response.json()
            
            rates = exchange_data.get('rates', {})
            kzt = rates.get('KZT')
            rub = rates.get('RUB')
            eur = rates.get('EUR')
            
            current_time = time_data.get('dateTime')
            
            @sync_to_async
            def get_blog_stats():
                return {
                    "total_posts": Post.objects.count(),
                    "total_comments": Comment.objects.count(),
                    "total_users": User.objects.count()
                }
            
            blog_stats = await get_blog_stats()
            
            return Response({
                "blog": blog_stats,
                "exchange_rates": {
                    "KZT": kzt,
                    "RUB": rub,
                    "EUR": eur
                },
                "current_time": current_time
            })
