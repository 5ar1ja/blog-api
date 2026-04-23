import pytz
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .managers import UserManager

def validate_timezone(value):
    if value not in pytz.all_timezones:
        raise ValidationError(_("%(value)s is not a valid timezone"), params={"value": value})

class User(AbstractUser, PermissionsMixin):
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ru', 'Russian'),
        ('kk', 'Kazakh'),
    ]
    language = models.CharField(
        max_length=5, 
        choices=LANGUAGE_CHOICES, 
        default='en',
        verbose_name=_("Preferred Language")
    )
    timezone = models.CharField(
        max_length=50, 
        default='UTC',
        validators=[validate_timezone],
        verbose_name=_("Timezone")
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self) -> str:
        return self.email