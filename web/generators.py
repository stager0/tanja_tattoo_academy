import json
import random
import secrets
from datetime import datetime, timedelta
from string import ascii_uppercase


def generate_reset_password_code(length=6) -> str:
    return "".join(str(secrets.randbelow(10)) for _ in range(length))

def generate_subscribe_code(length=14):
    code = ""
    for _ in range(length):
        if len(code) == 4 or len(code) == 9:
            code += "-"
        else:
            code += random.choice(ascii_uppercase)
    return code

def generate_fixture_messages(length=10001):
    list_result = []
    base_time = datetime(2025, 7, 14, 14, 0, 0)

    for i in range(81, length):
        new_time = base_time + timedelta(seconds=1)
        formated_time = new_time.isoformat() + "Z"

        if i % 2 == 0:
            list_result.append({
                "model": "web.message",
                "pk": i,
                "fields": {
                    "chat": 13,
                    "text": "Добрий день! У мене не виходить рівний контур на штучній шкірі, голка гуляє. Що я роблю не так?",
                    "user": 16,
                    "image": None,
                    "date": formated_time,
                    "is_read_user": False,
                    "is_read_admin": True,
                    "from_admin": True
                }
            })
        else:
            list_result.append({
                "model": "web.message",
                "pk": i,
                "fields": {
                    "chat": 13,
                    "text": "Вітаю, Олено! Це часта проблема. Спробуйте три речі: 1. Збільшіть натяг шкіри другою рукою. 2. Зменшіть виліт голки.",
                    "user": 16,
                    "image": None,
                    "date": formated_time,
                    "is_read_user": True,
                    "is_read_admin": False,
                    "from_admin": False
                }
            })

    with open("message.json", "w", encoding="utf8") as f:
        json.dump(list_result, f, ensure_ascii=False, indent=2)
    print("success")
