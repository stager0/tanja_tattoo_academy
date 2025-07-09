import secrets

def generate_reset_password_code(length=6) -> str:
    return "".join(str(secrets.randbelow(10)) for _ in range(length))
