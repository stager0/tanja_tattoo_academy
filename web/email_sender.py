import os
from urllib.parse import urljoin

from dotenv import load_dotenv
from mailjet_rest import Client

load_dotenv()

api_secret = os.getenv("API_SECRET")
api_key = os.getenv("API_KEY")

mailjet = Client(auth=(api_key, api_secret), version="v3.1")

app_name = "Tanja Tattoo"


def send_password_change_email(email: str, full_name: str, activation_code: str) -> None:
    reset_link = urljoin(os.getenv("URL_BASE"), "/accounts/change_password/")
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "andriishtaher@gmail.com",
                    "Name": "Tanja Tattoo"
                },
                "To": [
                    {
                        "Email": email,
                        "Name": full_name
                    }
                ],
                "Subject": f"Код для скидання пароля - {app_name}",
                "TextPart": f"""
                    Вітаємо, {full_name}!

                    Ми отримали запит на скидання пароля для вашого акаунту в {app_name}.

                    Ваш код для відновлення: {activation_code}
                    Цей код дійсний протягом 15 хвилин.

                    Щоб скинути пароль, перейдіть за посиланням: {reset_link}

                    Якщо ви не надсилали цей запит, просто проігноруйте даний лист.
                """,
                "HTMLPart": f"""
                    <!DOCTYPE html>
                    <html lang="uk">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Код для скидання пароля</title>
                        <style>
                            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
                            body {{
                                margin: 0;
                                padding: 0;
                                width: 100% !important;
                            }}
                        </style>
                    </head>
                    <body style="margin: 0; padding: 0; font-family: 'Montserrat', Arial, sans-serif; background-color: #121212;">
                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                            <tr>
                                <td align="center" style="padding: 40px 15px;">
                                    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                                        <tr>
                                            <td align="center" style="padding: 0 0 30px 0;">
                                                <h1 style="font-size: 32px; font-weight: 700; color: #FF8C00; margin: 0; font-family: 'Montserrat', Arial, sans-serif;">
                                                    Tanja Tattoo
                                                </h1>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td bgcolor="#1E1E1E" style="padding: 40px 30px; border-radius: 12px; border-top: 4px solid #FF8C00;">
                                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                                    <tr>
                                                        <td style="color: #FF8C00; font-family: 'Montserrat', Arial, sans-serif; font-size: 24px; font-weight: 700; text-align: center; padding-bottom: 25px;">
                                                            Запит на відновлення пароля
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="color: #E0E0E0; font-family: 'Montserrat', Arial, sans-serif; font-size: 18px; line-height: 1.6; text-align: center; padding-bottom: 15px;">
                                                            Вітаємо, {full_name}!
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 0 0 15px 0; color: #E0E0E0; font-family: 'Montserrat', Arial, sans-serif; font-size: 16px; line-height: 1.6; text-align: center;">
                                                            Ми отримали запит на скидання пароля. Використайте код нижче, щоб продовжити.
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td align="center" style="padding: 15px 0 25px 0;">
                                                            <p style="font-family: 'Montserrat', Arial, sans-serif; font-size: 32px; font-weight: 700; color: #FF8C00; background-color: #2a2a2a; margin: 0; padding: 15px 35px; border-radius: 8px; letter-spacing: 5px; display: inline-block;">
                                                                {activation_code}
                                                            </p>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="text-align: center; padding-bottom: 25px;">
                                                             <a href="{reset_link}" style="color: #FF8C00; text-decoration: underline; font-size: 14px;">Або перейдіть за цим посиланням, щоб скинути пароль</a>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 20px 0 0 0; color: #757575; font-family: 'Montserrat', Arial, sans-serif; font-size: 12px; line-height: 1.5; text-align: center;">
                                                            Код дійсний протягом 15 хвилин. Якщо ви не надсилали цей запит, будь ласка, проігноруйте цей лист.
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td align="center" style="padding: 30px 0 0 0;">
                                                <p style="margin: 0; color: #757575; font-size: 12px;">
                                                    &copy; 2025 Tanja Tattoo Studio. Всі права захищено.
                                                </p>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </body>
                    </html>
                    """
            }
        ]
    }

    mailjet.send.create(data=data)


def send_after_register_email(email: str, full_name: str):
    kit_form_link = urljoin(os.getenv("URL_BASE"), "/platform/box_application/")
    text_part = f"""
    Ласкаво просимо до Tanja Tattoo, {full_name}!

    Дякуємо за реєстрацію. Ваш код підписки успішно активовано та прив'язаний до вашого акаунту.

    Якщо ваша підписка це дозволяє, ви можете заповнити форму на сайті, щоб отримати свій ексклюзивний тату-набір.

    Перейти до форми: {kit_form_link}

    Дякуємо, що ви з нами!
    Команда Tanja Tattoo
    """

    html_part = f"""
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ласкаво просимо до Tanja Tattoo!</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
            body {{
                margin: 0;
                padding: 0;
                width: 100% !important;
            }}
        </style>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Montserrat', Arial, sans-serif; background-color: #121212;">
        <table border="0" cellpadding="0" cellspacing="0" width="100%">
            <tr>
                <td align="center" style="padding: 40px 15px;">
                    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                        <tr>
                            <td align="center" style="padding: 0 0 30px 0;">
                                <h1 style="font-size: 32px; font-weight: 700; color: #FF8C00; margin: 0; font-family: 'Montserrat', Arial, sans-serif;">
                                    Tanja Tattoo
                                </h1>
                            </td>
                        </tr>
                        <tr>
                            <td bgcolor="#1E1E1E" style="padding: 40px 30px; border-radius: 12px; border-top: 4px solid #FF8C00;">
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td style="color: #ffffff; font-family: 'Montserrat', Arial, sans-serif; font-size: 24px; font-weight: 700; text-align: center;">
                                            Ласкаво просимо, {full_name}!
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 20px 0 30px 0; color: #E0E0E0; font-family: 'Montserrat', Arial, sans-serif; font-size: 16px; line-height: 1.6; text-align: center;">
                                            Дякуємо за реєстрацію! Ваш код підписки успішно активовано та прив'язаний до вашого акаунту. Тепер вам доступні всі переваги нашої спільноти.
                                        </td>
                                    </tr>
                                    <tr><td style="padding: 10px 0;"><hr style="border: 0; border-top: 1px solid #444;"></td></tr>
                                    <tr>
                                        <td style="padding: 20px 0 20px 0; color: #E0E0E0; font-family: 'Montserrat', Arial, sans-serif; font-size: 16px; line-height: 1.6; text-align: center;">
                                            <b style="color: #FF8C00;">Ваш Тату-Набір</b><br>
                                            Якщо ваша підписка це дозволяє, ви можете заповнити форму на сайті, щоб отримати свій ексклюзивний тату-набір.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td align="center" style="padding: 10px 0 20px 0;">
                                            <a href="{kit_form_link}" target="_blank" style="font-size: 16px; font-family: 'Montserrat', Arial, sans-serif; font-weight: 700; color: #121212; text-decoration: none; border-radius: 8px; padding: 15px 35px; background-color: #FF8C00; display: inline-block;">
                                                Заповнити форму
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td align="center" style="padding: 30px 0 0 0;">
                                <p style="margin: 0; color: #757575; font-size: 12px;">
                                    &copy; {2025} Tanja Tattoo Studio. Всі права захищено.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    data = {
        'Messages': [
            {
                "From": {
                    "Email": "andriishtaher@gmail.com",
                    "Name": "Tanja Tattoo"
                },
                "To": [
                    {
                        "Email": email,
                        "Name": full_name
                    }
                ],
                "Subject": "Ласкаво просимо до Tanja Tattoo!",
                "TextPart": text_part,
                "HTMLPart": html_part
            }
        ]
    }

    mailjet.send.create(data=data)
