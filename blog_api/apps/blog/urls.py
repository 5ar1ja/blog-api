from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, PostStreamView

router = DefaultRouter()
router.register(r"", PostViewSet, basename="posts")

urlpatterns = [
    path("stream/", PostStreamView.as_view(), name="post-stream"),
    path("", include(router.urls)),
]