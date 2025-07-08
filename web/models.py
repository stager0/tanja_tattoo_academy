from web.custom_auth_user_manager import EmailAbstractUser


class UserModel(EmailAbstractUser):
    def __str__(self):
        return self.email