from django.db import models

from auth.custom_auth_user_manager import EmailAbstractUser


class UserModel(EmailAbstractUser):
    def __str__(self):
        return self.email