import os

from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from .custom_auth_user_manager import EmailAbstractUser

# used for change password.
class ResetCode(models.Model):
    code = models.CharField(max_length=6, validators=[MinLengthValidator(6)])
    user_email = models.EmailField(blank=False, null=False)
    is_activated = models.BooleanField(default=False, blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now, null=True, blank=True)

    def __str__(self):
        return self.code


class SubscribeChoices(models.TextChoices):
    base = "base"
    pro = "pro"
    master = "master"

# subscribe code
class Code(models.Model):
    code = models.CharField(max_length=14, unique=True, validators=[MinLengthValidator(14)])
    is_activated = models.BooleanField(default=False, null=True, blank=True)
    activated_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    tariff = models.CharField(choices=SubscribeChoices.choices, max_length=10, default="base") #------------> DELETE
    start_box_coupon_is_activated = models.BooleanField(default=False, null=True, blank=True)


def profile_avatar(instance, filename):
    filename_end = filename.split(".")[-1]
    if filename_end not in ["jpg", "jpeg", "png", "webp"]:
        raise ValueError("File must be photo!")
    filename_slug = slugify(instance.get_full_name()) or "user"
    return f"user_avatars/{instance.id}_{filename_slug}.{filename_end}"

# user
class UserModel(EmailAbstractUser):
    code = models.ForeignKey(Code, related_name="users", on_delete=models.CASCADE, null=True, blank=True) # ---------------> TO DELETE BEFORE PROD!!!!!!!!!!
    phone = models.CharField(max_length=13, validators=[MinLengthValidator(13)], blank=True, null=True)
    avatar = models.ImageField(upload_to=profile_avatar, blank=True, default="user_avatars/base_icon.png")
    last_activity = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Chat(models.Model):
    user = models.OneToOneField(UserModel, related_name="chats", on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now, null=True, blank=True)


# for chat
class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    text = models.CharField(max_length=512, null=False, blank=False)
    user = models.ForeignKey(UserModel, related_name="messages", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="message_images/", blank=True, null=True)
    date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    is_read_user = models.BooleanField(default=False, blank=True, null=True)
    is_read_admin = models.BooleanField(default=False, blank=True, null=True)
    from_admin = models.BooleanField(default=False, blank=True, null=True)


# Lectures
class Lecture(models.Model):
    lecture_name = models.CharField(max_length=100)
    under_name = models.CharField(max_length=60)
    position_number = models.IntegerField(blank=True, null=True)
    video_url = models.URLField(unique=False)
    lecture = models.CharField(max_length=712, blank=True, null=True, default="До цього уроку наразі немає лекції.")
    homework = models.CharField(max_length=400, blank=True, null=True, default="До цього уроку наразі немає ДЗ.")


# Users homeworks
class HomeWork(models.Model):
    lecture = models.ForeignKey(Lecture, related_name="home_works", on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(UserModel, related_name="home_works", on_delete=models.CASCADE)
    was_checked = models.BooleanField(default=False, null=True, blank=True)
    image = models.ImageField(upload_to="homework_images", default="system_files/not_found.jpeg", null=True, blank=True)
    date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    text = models.CharField(max_length=512, null=True, blank=True, default="Користувач відправив дз без запитань.")


class HomeWorkReview(models.Model):
    homework = models.ForeignKey(HomeWork, related_name="reviews", on_delete=models.CASCADE)
    review_text = models.CharField(max_length=155, blank=True, null=True)
    is_approved = models.BooleanField(default=False, blank=True, null=True)
    data = models.DateTimeField(default=timezone.now, null=True, blank=True)


class StartBox(models.Model):
    full_name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    user = models.ForeignKey(UserModel, related_name="start_boxes", on_delete=models.SET_NULL, null=True)
    phone = models.CharField(max_length=20)
    comments = models.CharField(max_length=200, blank=True, null=True)
    is_sent = models.BooleanField(default=False, blank=True, null=True)
    sent_date = models.DateTimeField(blank=True, null=True)


class LecturesCounter(models.Model):
    lecture = models.ForeignKey(Lecture, related_name="counter", on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, related_name="counter", on_delete=models.CASCADE)
