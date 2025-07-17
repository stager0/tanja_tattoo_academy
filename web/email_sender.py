import os
from datetime import datetime
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
    current_year = datetime.now().year

    # Покращена текстова версія
    text_part = f"""
        Привіт, {full_name}!

        Ми отримали запит на скидання пароля для вашого акаунту в {app_name}.
        Якщо це були не ви, просто проігноруйте цей лист.

        Ваш код для відновлення: {activation_code}
        (Цей код дійсний протягом 15 хвилин)

        Щоб скинути пароль, натисніть на посилання: {reset_link}

        З повагою,
        Команда {app_name}
    """

    html_part = f"""
    <!DOCTYPE html>
    <html lang="uk">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Відновлення пароля</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;900&family=Megrim&display=swap');
        body {{ margin: 0; padding: 0; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; background-color: #0d0d0d; }}
        table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
        a {{ text-decoration: none; }}
    </style>
    </head>
    <body style="margin: 0; padding: 0; background-color: #0d0d0d;">
    <center>
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
            <tr>
                <td align="center" style="padding: 40px 0;">
                    <h1 style="margin: 0; font-family: 'Megrim', cursive; font-size: 36px; font-weight: 400; color: #f5f5f5;">
                        Tanja<span style="font-family: 'Montserrat', sans-serif; font-size: 26px; font-weight: 900; color: #ff4500;">Tattoo</span>
                    </h1>
                </td>
            </tr>

            <tr>
                <td style="background-color: #1a1a1a; border-radius: 16px; border: 1px solid #333333; padding: 40px;">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <td align="center" style="font-family: 'Montserrat', sans-serif; font-size: 26px; font-weight: 700; color: #f5f5f5;">
                                Відновлення пароля
                            </td>
                        </tr>
                        <tr>
                            <td align="center" style="padding: 20px 0; font-family: 'Montserrat', sans-serif; font-size: 16px; line-height: 1.7; color: #a0a0a0;">
                                Привіт, {full_name}.<br>Ми отримали запит на скидання пароля для вашого акаунту. Натисніть кнопку нижче, щоб встановити новий пароль.
                            </td>
                        </tr>

                        <tr>
                            <td align="center" style="padding: 20px 0;">
                                <a href="{reset_link}" target="_blank" style="font-family: 'Montserrat', sans-serif; font-weight: 600; font-size: 16px; color: #f5f5f5; background-color: #ff4500; border-radius: 50px; padding: 15px 40px; display: inline-block; text-decoration: none;">
                                    Скинути пароль
                                </a>
                            </td>
                        </tr>

                        <tr><td style="padding: 20px 0;"><hr style="border: 0; border-top: 1px solid #333333;"></td></tr>

                        <tr>
                            <td align="center" style="font-family: 'Montserrat', sans-serif; font-size: 14px; line-height: 1.7; color: #a0a0a0;">
                                Якщо кнопка не працює, скопіюйте цей код:
                            </td>
                        </tr>
                        <tr>
                            <td align="center" style="padding: 10px 0 20px 0;">
                                 <p style="margin: 0; font-family: 'Montserrat', sans-serif; font-size: 20px; font-weight: 700; color: #f5f5f5; letter-spacing: 3px; background-color: #0d0d0d; padding: 10px 20px; border-radius: 8px; border: 1px solid #333333;">
                                    {activation_code}
                                </p>
                            </td>
                        </tr>

                        <tr>
                            <td align="center" style="font-family: 'Montserrat', sans-serif; font-size: 12px; line-height: 1.7; color: #a0a0a0; padding-top: 20px;">
                                Цей запит дійсний протягом 15 хвилин. Якщо ви його не створювали, просто проігноруйте цей лист — ваш акаунт у безпеці.
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            <tr>
                <td align="center" style="font-family: 'Montserrat', sans-serif; font-size: 12px; color: #a0a0a0; padding: 40px 15px;">
                    &copy; {current_year} {app_name}. Всі права захищено.
                </td>
            </tr>
        </table>
    </center>
    </body>
    </html>
    """

    data = {
        'Messages': [
            {
                "From": {
                    "Email": f"{os.getenv('EMAIL_FIRST_PART')}@gmail.com",
                    "Name": app_name
                },
                "To": [
                    {
                        "Email": email,
                        "Name": full_name
                    }
                ],
                "Subject": f"Відновлення пароля для {app_name}",
                "TextPart": text_part,
                "HTMLPart": html_part
            }
        ]
    }

    mailjet.send.create(data=data)


def send_email_subscribe_code(email: str, code: str, full_name: str):
    register_link = urljoin(os.getenv("URL_BASE"), "/register")
    current_year = datetime.now().year
    text_part = f"""
    Вітаємо у Tanja Tattoo Academy, {full_name}!

    Ваш платіж успішно отримано. Дякуємо за довіру!

    Це ваш унікальний код доступу до курсу:
    {code}

    Щоб почати навчання, просто зареєструйтеся на нашій платформі, ввівши цей код.

    Регістрація за посиланням: {register_link}
    
    (Використати код можливо лише 1 раз.)

    До зустрічі на курсі!
    Команда Tanja Tattoo
    """

    html_part = f"""
    <!DOCTYPE html>
    <html lang="uk">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Ваш доступ до Tanja Tattoo Academy</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;900&display=swap');

        body {{
            margin: 0;
            padding: 0;
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
            background-color: #0d0d0d;
        }}
        table, td {{
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
        }}
        img {{
            -ms-interpolation-mode: bicubic;
            border: 0;
        }}
        a {{
            text-decoration: none;
        }}
    </style>
    </head>
    <body style="margin: 0; padding: 0; background-color: #0d0d0d;">
    <center>
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
            <tr>
                <td align="center" style="padding: 40px 0;">
                    <h1 style="margin: 0; font-family: 'Megrim', cursive; font-size: 36px; font-weight: 400; color: #f5f5f5;">
                        Tanja<span style="font-family: 'Montserrat', sans-serif; font-size: 26px; font-weight: 900; color: #ff4500;">Tattoo</span>
                    </h1>
                </td>
            </tr>

            <tr>
                <td style="background-color: #1a1a1a; border-radius: 16px; border: 1px solid #333333; padding: 40px; box-shadow: 0 0 30px rgba(255, 69, 0, 0.2);">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <td align="center" style="font-family: 'Montserrat', sans-serif; font-size: 26px; font-weight: 700; color: #f5f5f5;">
                                Вітаємо, {full_name}!
                            </td>
                        </tr>
                        <tr>
                            <td align="center" style="padding: 20px 0; font-family: 'Montserrat', sans-serif; font-size: 16px; line-height: 1.7; color: #a0a0a0;">
                                Дякуємо за покупку курсу! Ми на крок ближче до того, щоб перетворити вашу мрію на реальність. Нижче ваш персональний ключ до світу тату.
                            </td>
                        </tr>
                        <tr>
                            <td align="center" style="padding: 25px 0;">
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr><td align="center" style="font-family: 'Montserrat', sans-serif; font-size: 14px; color: #a0a0a0; padding-bottom: 10px;">Ваш унікальний код доступу:</td></tr>
                                    <tr>
                                        <td align="center" style="background-color: #0d0d0d; border: 2px dashed #ff4500; border-radius: 12px; padding: 20px;">
                                            <p style="margin: 0; font-family: 'Montserrat', sans-serif; font-size: 24px; font-weight: 700; color: #f5f5f5; letter-spacing: 4px;">
                                                {code}
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td align="center" style="padding: 25px 0; font-family: 'Montserrat', sans-serif; font-size: 16px; line-height: 1.7; color: #a0a0a0;">
                                <b>Що далі?</b><br>
                                Просто натисніть на кнопку нижче, пройдіть просту реєстрацію та введіть цей код у відповідне поле, щоб активувати доступ до курсу.
                            </td>
                        </tr>
                        <tr>
                            <td align="center" style="padding: 15px 0 25px 0;">
                                <a href="{register_link}" target="_blank" style="font-family: 'Montserrat', sans-serif; font-weight: 600; font-size: 16px; color: #f5f5f5; background-color: #ff4500; border-radius: 50px; padding: 15px 40px; display: inline-block; text-decoration: none;">
                                    Зареєструватися з кодом і почати навчання
                                </a>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            <tr>
                <td align="center" style="padding: 40px 0 10px 0;">
                    </td>
            </tr>
            <tr>
                <td align="center" style="font-family: 'Montserrat', sans-serif; font-size: 12px; color: #a0a0a0; padding: 0 15px 40px 15px;">
                    Ви отримали цей лист, оскільки придбали курс на сайті Tanja Tattoo Academy.
                    <br>
                    &copy; {current_year} Tanja Tattoo. Всі права захищено.
                </td>
            </tr>
        </table>
    </center>
    </body>
    </html>
    """
    data = {
        "Messages": [
            {
                "From": {
                    "Email": f"{os.getenv('EMAIL_FIRST_PART')}@gmail.com",
                    "Name": "Tanja Tattoo Academy"
                },
                "To": [
                    {
                        "Email": email,
                        "Name": full_name
                    }
                ],
                "Subject": "Вітаємо у Tanja Tattoo Academy",
                "TextPart": text_part,
                "HTMLPart": html_part
            }
        ]
    }

    mailjet.send.create(data=data)


def send_after_register_email(email: str, full_name: str):
    kit_form_link = urljoin(os.getenv("URL_BASE"), "/platform/box_application/")
    dashboard_link = urljoin(os.getenv("URL_BASE"), "/platform/dashboard/")
    current_year = datetime.now().year
    text_part = f"""
    Ласкаво просимо до Академії, {full_name}!

    Ваш доступ активовано! Тепер ви офіційно є частиною нашої творчої спільноти. Всі уроки та матеріали вже чекають на вас в особистому кабінеті.

    Перейти до навчання: {dashboard_link}

    Якщо ваш тариф передбачає тату-бокс, не забудьте заповнити заявку на його отримання.
    Заповнити форму для боксу: {kit_form_link}

    Бажаємо натхнення!
    Команда Tanja Tattoo
    """

    # Покращена HTML версія
    html_part = f"""
    <!DOCTYPE html>
    <html lang="uk">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ласкаво просимо до Tanja Tattoo Academy!</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;900&family=Megrim&display=swap');
        body {{ margin: 0; padding: 0; -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; background-color: #0d0d0d; }}
        table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
        img {{ -ms-interpolation-mode: bicubic; border: 0; }}
        a {{ text-decoration: none; }}
    </style>
    </head>
    <body style="margin: 0; padding: 0; background-color: #0d0d0d;">
    <center>
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
            <tr>
                <td align="center" style="padding: 40px 0;">
                    <h1 style="margin: 0; font-family: 'Megrim', cursive; font-size: 36px; font-weight: 400; color: #f5f5f5;">
                        Tanja<span style="font-family: 'Montserrat', sans-serif; font-size: 26px; font-weight: 900; color: #ff4500;">Tattoo</span>
                    </h1>
                </td>
            </tr>

            <tr>
                <td style="background-color: #1a1a1a; border-radius: 16px; border: 1px solid #333333; padding: 40px;">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <td align="center" style="font-family: 'Montserrat', sans-serif; font-size: 26px; font-weight: 700; color: #f5f5f5;">
                                Все готово, {full_name}!
                            </td>
                        </tr>
                        <tr>
                            <td align="center" style="padding: 20px 0; font-family: 'Montserrat', sans-serif; font-size: 16px; line-height: 1.7; color: #a0a0a0;">
                                Ваш код доступу успішно активовано! Ласкаво просимо до <b style="color: #f5f5f5;">Tanja Tattoo Academy</b>. Всі двері у світ тату-мистецтва тепер відчинені для вас.
                            </td>
                        </tr>
                        <tr>
                            <td align="center" style="padding: 20px 0 30px 0;">
                                <a href="{dashboard_link}" target="_blank" style="font-family: 'Montserrat', sans-serif; font-weight: 600; font-size: 16px; color: #f5f5f5; background-color: #ff4500; border-radius: 50px; padding: 15px 40px; display: inline-block; text-decoration: none;">
                                    Перейти до навчання
                                </a>
                            </td>
                        </tr>

                        <tr><td style="padding: 10px 0;"><hr style="border: 0; border-top: 1px solid #333333;"></td></tr>

                        <tr>
                            <td align="center" style="padding: 30px 0 0 0;">
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td align="center" style="font-family: 'Montserrat', sans-serif; font-size: 18px; font-weight: 700; color: #f5f5f5; padding-bottom: 10px;">
                                            Не забудьте про ваш Тату-Бокс!
                                        </td>
                                    </tr>
                                    <tr>
                                        <td align="center" style="font-family: 'Montserrat', sans-serif; font-size: 15px; line-height: 1.7; color: #a0a0a0;">
                                            Якщо ваш тариф включає стартовий набір, заповніть коротку форму, і ми надішлемо його вам якомога швидше.
                                        </td>
                                    </tr>
                                    <tr>
                                        <td align="center" style="padding: 20px 0 0 0;">
                                            <a href="{kit_form_link}" target="_blank" style="font-family: 'Montserrat', sans-serif; font-weight: 600; font-size: 15px; color: #ff4500; text-decoration: underline;">
                                                Заповнити адресу доставки &rarr;
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            <tr>
                <td align="center" style="font-family: 'Montserrat', sans-serif; font-size: 12px; color: #a0a0a0; padding: 40px 15px;">
                    &copy; {current_year} Tanja Tattoo. Всі права захищено.
                </td>
            </tr>
        </table>
    </center>
    </body>
    </html>
    """

    data = {
        'Messages': [
            {
                "From": {
                    "Email": f"{os.getenv('EMAIL_FIRST_PART')}@gmail.com",
                    "Name": "Tanja Tattoo Academy"
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
