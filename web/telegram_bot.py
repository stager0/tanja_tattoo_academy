import json
import os

import telebot
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

from tattoo_academy.settings import TELEGRAM_BOT_TOKEN
from web.models import UserModel

load_dotenv()

bot = telebot.TeleBot(token=settings.TELEGRAM_BOT_TOKEN)


def set_telegram_webhook():
    import requests
    response = requests.post(
        f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_KEY')}/setWebhook",
        json={"url": f"https://{os.getenv('HOST')}/telegram_webhook/{os.getenv('TELEGRAM_BOT_KEY')}/"}
        )
    print(response.json())


@csrf_exempt
def webhook_telegram(request, token: str = None):
    if request.method == "POST":
        if token != TELEGRAM_BOT_TOKEN:
            return HttpResponseForbidden("Invalid Token")
        update_data = json.loads(request.body.decode("utf-8"))

        if update_data:
            try:
                message = update_data["message"]
                text = message.get("text")
                chat_id = int(message.get("chat").get("id"))
                print(chat_id)

                if text.startswith("/", 0):
                    if text.strip().startswith("/start"):
                        bot.send_message(
                            chat_id=chat_id,
                            text="📧 Введіть, будь ласка, email, прив'язаний до вашого облікового запису."
                        )
                        return JsonResponse({"status": "ok"})
                    else:
                        bot.send_message(
                            chat_id=chat_id,
                            text="😅 Хмм... Я не знаю такої команди. Можливо, пальці послизнулись? 🤔\nВведіть /start, щоб почати спілкування з ботом."
                        )
                        return JsonResponse({"status": "ok"})
                if "@" in text and ".com" in text:
                    user = UserModel.objects.filter(Q(telegram_chat_id=chat_id) | Q(email=text.strip().lower())).first()
                    if user and not user.telegram_chat_id:
                        user.telegram_chat_id = chat_id
                        user.save()
                        if not user.is_superuser:
                            bot.send_message(
                                chat_id=chat_id,
                                text=(
                                    "✅ Ваш обліковий запис успішно прив'язано!\n\n"
                                    "Тепер ви будете отримувати сповіщення в цей чат, коли ментор відповість вам в чаті на платформі або перевірить домашнє завдання.\n\n"
                                    "🧿 Бажаємо успіхів у навчанні та натхнення на шляху до майстерності в тату!"
                                )
                            )
                            return JsonResponse({"status": "ok"})
                        else:
                            bot.send_message(
                                chat_id=chat_id,
                                text=(
                                    "✅ Ваш обліковий запис успішно прив'язано!\n\n"
                                    "Тепер ви будете отримувати сповіщення в цей чат, коли учні будуть відповідати вам в чаті на платформі або надсилати домашнє завдання.\n\n"
                                )
                            )
                            return JsonResponse({"status": "ok"})

                    elif not user:
                        bot.send_message(
                            chat_id=chat_id,
                            text=(
                                "😔 На жаль, ми не знайшли ваш обліковий запис.\n\n"
                                "Якщо ви ще не з нами — приєднуйтесь до курсу за посиланням:\n"
                                f"https://{os.getenv('HOST')}\n\n"
                                "✨ Стартуйте свій шлях у світі тату вже сьогодні!"
                            )
                        )
                        return JsonResponse({"status": "ok"})
                    elif user.telegram_chat_id:
                        bot.send_message(
                            chat_id=chat_id,
                            text=(
                                "😔 Цей акаунт вже прив’язаний до іншого профілю.\n\n"
                                "Якщо ти вважаєш, що сталася помилка — напиши в підтримку."
                            )
                        )
                        return JsonResponse({"status": "ok"})

                if text:
                    if UserModel.objects.filter(telegram_chat_id=chat_id).exists():
                        bot.send_message(
                            chat_id=chat_id,
                            text=(
                                "😅 Ой, здається, це повідомлення надіслано випадково?\n"
                                "Не хвилюйтеся — просто очікуйте на сповіщення від мене. "
                                "Я повідомлю вас, щойно на платформі з’явиться нове повідомлення або відповідь від ментора. 📩"
                            )
                        )
                        return JsonResponse({"status": "ok"})
                    else:
                        bot.send_message(
                        chat_id=chat_id,
                        text="😅 Хмм... Я не знаю такої команди. Можливо, пальці послизнулись? 🤔\nВведіть /start, щоб почати спілкування з ботом."
                        )
                        return JsonResponse({"status": "ok"})
                return JsonResponse({"status": "ok"})
            except Exception as e:
                print(e)
        return JsonResponse({"status": "400"})


def send_message_in_telegram(text: str, chat_id: str = 0):
    user = UserModel.objects.filter(telegram_chat_id=chat_id).first()
    if user:
        bot.send_message(chat_id=int(chat_id), text=text)
    return JsonResponse({"status": "ok"})
