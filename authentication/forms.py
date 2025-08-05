from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.validators import MinLengthValidator

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
