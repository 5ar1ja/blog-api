import logging

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from rest_framework import viewsets, status
from rest_framework.response import Response

from .serializers import RegisterSerializer

logger = logging.getLogger(__name__)
# Create your views here.

@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='create')
class UserRegistrationViewSet(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        logger.info("Registration attempt for email: %s", request.data.get("email"))
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user=serializer.save()
            #logging success
            logger.info('User registred: %s', user.email)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        logger.warning('Registration failed for email: %s', request.data.get('email'))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)