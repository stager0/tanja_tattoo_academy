import random
import secrets
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
