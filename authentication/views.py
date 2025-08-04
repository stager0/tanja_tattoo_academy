from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import CreateView

from authentication.forms import CustomRegisterForm, PasswordChangeRequestForm, ChangePasswordForm
from authentication.models import UserModel
from web.email_sender import send_password_change_email, send_after_register_email
from web.generators import generate_reset_password_code
from web.models import ResetCode, Chat
from web.telegram_bot import send_message_in_telegram

UserModel = get_user_model()


class RegisterView(CreateView):
    form_class = CustomRegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        print(form)
        with transaction.atomic():
            try:
                code_obj = form.cleaned_data.get("code", None)
                if code_obj:
                    code_obj.is_activated = True
                    code_obj.activated_date = timezone.now()
                    code_obj.save()

                email = form.cleaned_data.get("email", "")
                full_name = form.cleaned_data.get("first_name", "") + " " + form.cleaned_data.get("last_name", "")
                if email and full_name:
                    send_after_register_email(email=email, full_name=full_name)

                self.object = form.save()

                Chat.objects.create(
                    user=self.object
                )
                mentor = UserModel.objects.filter(is_superuser=True).first()
                if mentor:
                    mentor_chat_id = mentor.telegram_chat_id if mentor.telegram_chat_id else None
                    if mentor_chat_id:
                        send_message_in_telegram(chat_id=mentor_chat_id,
                                                 text=f"Юзер '{full_name}' тільки що зареєструвався на платформі.")
                return super().form_valid(form)
            except Exception as e:
                print(e)
                response = HttpResponseRedirect(reverse("register"))
                response.status_code = 400
                return response

    def form_invalid(self, form):
        print("Форма не валидна")
        print(form.errors)
        return super().form_invalid(form)


class ChangePasswordRequestView(generic.FormView):
    form_class = PasswordChangeRequestForm
    template_name = "registration/change_password_request.html"
    success_url = reverse_lazy("email_sent_info")

    def form_valid(self, form):
        if form.cleaned_data["email"] is not None and form.cleaned_data["full_name"] is not None:
            email = form.cleaned_data.get("email")
            full_name = form.cleaned_data.get("full_name")
            code = generate_reset_password_code()
            ResetCode.objects.create(
                user_email=email,
                code=code,
            )
            user = UserModel.objects.filter(email=email).first()
            chat_id = None

            if user and user.telegram_chat_id:
                chat_id = user.telegram_chat_id

            if chat_id:
                send_message_in_telegram(
                    chat_id=chat_id,
                    text=(
                        "✉️ Хтось запросив код для зміни вашого пароля. Ми вже надіслали його на вашу електронну пошту.\n"
                        "Якщо це були не ви — просто проігноруйте це повідомлення. Ваш обліковий запис залишиться в безпеці. 🔒")
                )

            send_password_change_email(email=email, full_name=full_name, activation_code=code)
            return super().form_valid(form)

        else:
            return super().form_valid(form)


class ChangePasswordView(generic.FormView):
    form_class = ChangePasswordForm
    template_name = "registration/change_password.html"
    success_url = reverse_lazy("change_password_success")

    def form_valid(self, form):
        code = form.cleaned_data.get("code")
        password = form.cleaned_data.get("password1")

        try:
            code_obj = ResetCode.objects.get(code=code)

            if code_obj.is_activated:
                form.add_error('code', "На жаль, ваш код вже активований.")
                return self.form_invalid(form)

            if code_obj.created_date + timedelta(minutes=15) < timezone.now():
                form.add_error('code', "На жаль, ваш код прострочений.")
                return self.form_invalid(form)

            user = get_user_model().objects.get(email=code_obj.user_email)

        except (ResetCode.DoesNotExist, get_user_model().DoesNotExist):
            form.add_error('code', "Введений код недійсний або пов'язаний з ним акаунт не знайдено.")
            return self.form_invalid(form)

        user.set_password(password)
        user.save()

        code_obj.is_activated = True
        code_obj.save()

        if user and user.telegram_chat_id:
            send_message_in_telegram(
                chat_id=user.telegram_chat_id,
                text=(
                    "✅ Ваш пароль було успішно змінено!\n"
                    "Тепер ви можете використовувати свій акаунт з новими даними.\n"
                    "Якщо це були не ви — негайно зверніться в підтримку. 🔒"
                )
            )

        return super().form_valid(form)
