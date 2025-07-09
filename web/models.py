from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone

from .custom_auth_user_manager import EmailAbstractUser


class ResetCode(models.Model):
    code = models.CharField(max_length=6, validators=[MinLengthValidator(6)])
    user_email = models.EmailField(blank=False, null=False)
    is_activated = models.BooleanField(default=False, blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now, null=True, blank=True)


class Code(models.Model):
    code = models.CharField(max_length=14, unique=True, validators=[MinLengthValidator(14)])
    is_activated = models.BooleanField(default=False, null=True, blank=True)
    activated_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now, null=True, blank=True)


class UserModel(EmailAbstractUser):
    code = models.ForeignKey(Code, related_name="users", on_delete=models.CASCADE)
    phone = models.CharField(max_length=13, validators=[MinLengthValidator(13)], blank=True, null=True)

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

