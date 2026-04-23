from django.urls import path
from .views import NotificationListView, NotificationCountView, NotificationReadView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('count/', NotificationCountView.as_view(), name='notification-count'),
    path('read/', NotificationReadView.as_view(), name='notification-read-all'),
    path('read/<int:pk>/', NotificationReadView.as_view(), name='notification-read'),
]
