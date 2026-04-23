import logging
import pytz
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import translation

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Исправил опечатку 'felds' -> 'fields' и добавил новые поля
        fields = ("id", "email", "first_name", "last_name", "avatar", "language", "timezone")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    tokens = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
            "language",  # Добавлено
            "timezone",  # Добавлено
            "tokens",
        )

    def validate_timezone(self, value):
        if value not in pytz.all_timezones:
            # ТЗ требует 400 ошибку с четким сообщением
            raise serializers.ValidationError(_("Invalid IANA timezone identifier."))
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs["password_confirm"]:
            logger.info("Registration failure: passwords do not match")
            # Используем _() для перевода ошибки
            raise serializers.ValidationError({"password": _("Passwords must match.")})
        return attrs

    def create(self, validated_data: dict) -> User:
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        
        logger.info("User registered: %s", user.email)
        
        # Отправка Welcome Email согласно ТЗ
        self._send_welcome_email(user)
        
        return user

    def _send_welcome_email(self, user):
        """
        Отправляет письмо на языке, который пользователь выбрал при регистрации.
        """
        # ТЗ: Язык письма независим от текущего языка запроса
        with translation.override(user.language):
            subject = _("Welcome to our Blog!")
            context = {
                'first_name': user.first_name,
                'email': user.email
            }
            # ТЗ: Рендеринг из шаблона
            html_message = render_to_string('emails/welcome/body.html', context)
            
            try:
                send_mail(
                    subject=str(subject),
                    message='',  # Пустое тело, так как используем HTML
                    from_email=None, # Возьмет DEFAULT_FROM_EMAIL из settings
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                logger.error("Failed to send welcome email to %s: %s", user.email, str(e))

    def get_tokens(self, user: User) -> dict:
        refresh = RefreshToken.for_user(user)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}

# Новые сериализаторы для PATCH эндпоинтов из ТЗ
class LanguageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('language',)

class TimezoneUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('timezone',)
    
    def validate_timezone(self, value):
        if value not in pytz.all_timezones:
            raise serializers.ValidationError(_("Invalid IANA timezone identifier."))
        return value