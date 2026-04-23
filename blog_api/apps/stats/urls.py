from django.urls import path
from .views import StatsAPIView

urlpatterns = [
    path("", StatsAPIView.as_view(), name="stats"),
]
