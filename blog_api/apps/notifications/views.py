from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = request.user.notifications.all()[:50]
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class NotificationCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = request.user.notifications.filter(is_read=False).count()
        return Response({"unread_count": count})

class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        if pk:
            try:
                notification = request.user.notifications.get(pk=pk)
                notification.is_read = True
                notification.save()
                return Response({"status": "success"})
            except Notification.DoesNotExist:
                return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Mark all as read
            request.user.notifications.filter(is_read=False).update(is_read=True)
            return Response({"status": "all marked as read"})
