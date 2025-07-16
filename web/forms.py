import os

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator

from web.models import Code, Message, StartBox, UserModel, HomeWork, HomeWorkReview, Lecture
from web.validators import validate_phone_number, validate_subscribe_code


class CustomRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    code = forms.CharField(max_length=14, validators=[MinLengthValidator(14), validate_subscribe_code], required=True)
    phone = forms.CharField(required=False, validators=[validate_phone_number])

    def clean_code(self):
        code_str = self.cleaned_data.get("code")
        try:
            code = Code.objects.get(code=code_str)
            return code
        except Code.DoesNotExist:
            raise forms.ValidationError("Invalid code")

    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "email", "password1", "password2", "phone", "code"]


class PasswordChangeRequestForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            user = get_user_model().objects.get(email=email)
            return email
        except get_user_model().DoesNotExist:
            return None

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email", "")
        if email:
            user = get_user_model().objects.get(email=email)
            full_name = user.get_full_name()
            cleaned_data["full_name"] = full_name
        else:
            cleaned_data["full_name"] = None

        return cleaned_data


class ChangePasswordForm(forms.Form):
    code = forms.CharField(required=True, min_length=6, max_length=6)
    password1 = forms.CharField(required=True, min_length=8, max_length=50)
    password2 = forms.CharField(required=True, min_length=8, max_length=50)

    def clean_password1(self):
        validate_password(self.cleaned_data["password1"])
        return self.cleaned_data["password1"]

    def clean(self):
        cleaned_data = super().clean()
        pass1 = cleaned_data.get("password1", "")
        pass2 = cleaned_data.get("password2", "")

        if not pass1 or not pass2 or pass1 != pass2:
            raise forms.ValidationError("Паролі не співпадають.")

        return cleaned_data


class BoxApplicationForm(forms.ModelForm):
    class Meta:
        model = StartBox
        fields = ("full_name", "phone", "address", "comments")


class ProfileForm(forms.Form):
    avatar = forms.ImageField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False)
    current_password = forms.CharField(required=False)
    new_password = forms.CharField(required=False)
    confirm_new_password = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.current_hashed_password = kwargs.pop("hashed_current_password", "")
        self.user_id = kwargs.pop("user_id", "")
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get("current_password", "")
        new_password = self.cleaned_data.get("new_password", "")

        if self.current_hashed_password and current_password and new_password:
            if not check_password(current_password, self.current_hashed_password):
                raise forms.ValidationError("Недійсний пароль.")
            elif check_password(current_password, self.current_hashed_password):
                return current_password

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar", "")

        if avatar:
            if avatar.name.split(".")[-1] not in ["jpg", "jpeg", "png", "webp"]:
                raise forms.ValidationError("Аватар повинен бути фото формату.")
            user_avatar = UserModel.objects.get(id=self.user_id).avatar.path
            if os.path.isfile(user_avatar):
                os.remove(user_avatar)
        return avatar

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password", "")
        new_password_confirm = cleaned_data.get("confirm_new_password", "")

        if new_password != new_password_confirm or new_password is None or new_password_confirm is None:
            raise forms.ValidationError("Паролі не співпадають")
        if new_password and new_password_confirm:
            validate_password(new_password)
        return cleaned_data


class ChatForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["text", "image"]


class IndexForm(forms.Form):
    name = forms.CharField(required=True, max_length=70)
    contact_method = forms.CharField(required=True, max_length=70)
    contact_details = forms.CharField(required=True, max_length=80)


class LectureHomeworkUserForm(forms.ModelForm):
    image = forms.ImageField(required=True)
    text = forms.CharField(required=True)

    class Meta:
        model = HomeWork
        fields = ["image", "text"]


class ReviewTaskForm(forms.ModelForm):
    class Meta:
        model = HomeWorkReview
        fields = ["review_text"]


class LectureEditForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ["lecture_name", "under_name", "position_number", "video_url", "lecture", "homework"]
        widgets = {
            'lecture_name': forms.TextInput(attrs={'class': 'form-control'}),
            'under_name': forms.TextInput(attrs={'class': 'form-control'}),
            'position_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://googleusercontent.com/...'}),
            'lecture': forms.Textarea(),
            'homework': forms.Textarea(),
        }


class LectureCreateForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ["lecture_name", "under_name", "position_number", "video_url", "lecture", "homework"]
