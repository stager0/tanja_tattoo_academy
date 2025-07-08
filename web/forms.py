from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.validators import MinLengthValidator

from web.models import Code
from web.validators import validate_phone_number, validate_subscribe_code


class CustomRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    code = forms.CharField(max_length=14, validators=[MinLengthValidator(14), validate_subscribe_code], required=True)
    phone = forms.CharField(required=False, validators=[validate_phone_number])

    def clean_code(self):
        code_str = self.cleaned_data["code"]
        try:
            code = Code.objects.get(code=code_str)
            return code
        except Code.DoesNotExist:
            raise forms.ValidationError("Invalid code")

    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "email", "password1", "password2", "phone", "code"]
