from django.core.exceptions import ValidationError

from web.models import Code


def validate_phone_number(number: str) -> ValidationError | None:
    if not len(number) == 13 and (number[:4] == "+380" or number[:3] == "+49"):
        raise ValidationError("Phone number must be 13 symbols lang.")


def validate_subscribe_code(code: str) -> ValidationError | None:
    code = Code.objects.get(code=code)
    if not code or code.is_activated is True:
        raise ValidationError("Invalid code was provided.")
