from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from web.models import Message, StartBox, HomeWork, HomeWorkReview, Lecture

UserModel = get_user_model()

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
