from django import forms

from web.models import Code


def validate_phone_number(number: str) -> None:
    if number.startswith("+380") and len(number) != 13:
        raise forms.ValidationError("Номер телефону України має містити 13 символів (включаючи +).")
    elif number.startswith("+49") and len(number) != 13:
        raise forms.ValidationError("Німецький номер телефону має містити 13 символів.")
    elif not (number.startswith("+380") or number.startswith("+49")):
        raise forms.ValidationError("Номер має починатися з +380 або +49.")

def validate_subscribe_code(code: str) -> Code | None:
    code_obj = Code.objects.filter(code=code).first()
    return code_obj if code_obj else None
