from cloudinary_storage.storage import MediaCloudinaryStorage
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.text import slugify

from authentication.custom_auth_user_manager import EmailAbstractUser


def profile_avatar(instance, filename):
    filename_end = filename.split(".")[-1]
    if filename_end not in ["jpg", "jpeg", "png", "webp"]:
        raise ValueError("File must be photo!")
    filename_slug = slugify(instance.get_full_name()) or "user"
    return f"user_avatars/{instance.id}_{filename_slug}.{filename_end}"


class UserModel(EmailAbstractUser):
    code = models.OneToOneField("web.Code", related_name="users", on_delete=models.CASCADE, null=True, blank=True) # ---------------> TO DELETE BEFORE PROD!!!!!!!!!!
    phone = models.CharField(max_length=13, validators=[MinLengthValidator(13)], blank=True, null=True)
    avatar = models.ImageField(upload_to=profile_avatar, max_length=300, blank=True, storage=MediaCloudinaryStorage(), default="base_icon_k7nhiw")
    last_activity = models.DateTimeField(null=True, blank=True)
    telegram_chat_id = models.CharField(null=True, blank=True)

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
