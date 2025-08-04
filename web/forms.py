from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.validators import MinLengthValidator
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from web.models import Message, StartBox, HomeWork, HomeWorkReview, Lecture
from web.validators import validate_phone_number, validate_subscribe_code


UserModel = get_user_model()

class CustomRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    code = forms.CharField(max_length=14, validators=[MinLengthValidator(14)], required=True)
    phone = forms.CharField(required=False, validators=[validate_phone_number])

    def clean_code(self):
        code_str = self.cleaned_data.get("code")
        if not code_str:
            raise forms.ValidationError("Код не може бути порожнім.")
        try:
            code = validate_subscribe_code(code_str)
        except Exception as e:
            raise forms.ValidationError("Неприпустимий код.")
        if not code:
            raise forms.ValidationError("Неприпустимий або вже використаний код.")
        return code

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
    password1 = forms.CharField(required=True, min_length=8, max_length=50, widget=forms.PasswordInput())
    password2 = forms.CharField(required=True, min_length=8, max_length=50, widget=forms.PasswordInput())

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

# web/forms.py

class ProfileForm(forms.ModelForm):
    current_password = forms.CharField(label="Поточний пароль", required=False, widget=forms.PasswordInput)
    new_password1 = forms.CharField(label="Новий пароль", required=False, widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Підтвердження нового пароля", required=False, widget=forms.PasswordInput)

    class Meta:
        model = UserModel
        fields = ('first_name', 'last_name', 'email', 'phone', 'avatar')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Ваше ім\'я'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Ваше прізвище'}),
            'email': forms.EmailInput(),
            'phone': forms.TextInput(attrs={'placeholder': 'Ваш номер телефону'}),
            'avatar': forms.FileInput,
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields["email"].disabled = True

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")

        if 'avatar' in self.files:
            if avatar.size > 2 * 1024 * 1024:  # 2 MB
                raise forms.ValidationError("Розмір фото має бути максимум 2МБ.")
            if avatar.content_type not in ["image/jpeg", "image/png", "image/webp"]:
                raise forms.ValidationError("Аватар має бути файлом у форматі JPG, PNG або WEBP.")
        self.user.avatar.delete()
        return avatar

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")
        current_password = cleaned_data.get("current_password")

        if new_password1 or new_password2 or current_password:
            if not current_password:
                self.add_error('current_password', "Введіть поточний пароль, щоб встановити новий.")
            elif not self.user or not check_password(current_password, self.user.password):
                self.add_error('current_password', "Неправильний поточний пароль.")

            if not new_password1:
                self.add_error('new_password1', "Введіть новий пароль.")
            else:
                if new_password1 != new_password2:
                    self.add_error('new_password2', "Паролі не співпадають.")
                try:
                    validate_password(new_password1, self.user)
                except forms.ValidationError as e:
                    self.add_error('new_password1', e)

        return cleaned_data


class ChatForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["text", "image"]

    def clean_image(self):
        image = self.cleaned_data.get("image")

        if 'image' in self.files:
            if image.size > 4 * 1024 * 1024:  # 4 MB
                raise forms.ValidationError("Розмір фото має бути максимум 4МБ.")
            if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
                raise forms.ValidationError("Фото має бути файлом у форматі JPG, PNG або WEBP.")

        return image


class IndexForm(forms.Form):
    name = forms.CharField(required=True, max_length=70)
    contact_method = forms.CharField(required=True, max_length=70)
    contact_details = forms.CharField(required=True, max_length=80)


class LectureHomeworkUserForm(forms.ModelForm):
    image = forms.ImageField(required=False)
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
            'video_url': forms.URLInput(
                attrs={'class': 'form-control', 'placeholder': 'https://googleusercontent.com/...'}),
            'lecture': forms.Textarea(),
            'homework': forms.Textarea(),
        }


class LectureCreateForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ["lecture_name", "under_name", "position_number", "video_url", "lecture", "homework"]
