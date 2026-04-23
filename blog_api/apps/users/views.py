import logging
from .tasks import send_welcome_email
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .serializers import (
    RegisterSerializer, 
    LanguageUpdateSerializer, 
    TimezoneUpdateSerializer
)

logger = logging.getLogger(__name__)

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='create')
class AuthViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    # Мы объединяем регистрацию и настройки в один AuthViewSet
    # Но для регистрации используем RegisterSerializer
    def get_serializer_class(self):
        if self.action == 'create':
            return RegisterSerializer
        if self.action == 'set_language':
            return LanguageUpdateSerializer
        if self.action == 'set_timezone':
            return TimezoneUpdateSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        logger.info("Registration attempt for email: %s", request.data.get("email"))
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info('User registered: %s', user.email)
            
            # Offload welcome email to Celery
            send_welcome_email.delay(user.email, user.first_name)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        logger.warning('Registration failed for email: %s', request.data.get('email'))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH /api/auth/language/
    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated], url_path='language')
    def set_language(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Language updated successfully."}, status=status.HTTP_200_OK)

    # PATCH /api/auth/timezone/
    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated], url_path='timezone')
    def set_timezone(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Timezone updated successfully."}, status=status.HTTP_200_OK)