import os

from datetime import timedelta
from decimal import Decimal
from functools import wraps

import stripe.checkout
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Count, Max, OuterRef, Subquery, FloatField, IntegerField
from django.db.models.functions import Cast
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponseServerError, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic, View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView
from dotenv import load_dotenv

from web.email_sender import send_password_change_email, send_after_register_email, send_email_subscribe_code
from web.forms import CustomRegisterForm, PasswordChangeRequestForm, ChangePasswordForm, BoxApplicationForm, \
    ProfileForm, ChatForm, IndexForm, LectureHomeworkUserForm, ReviewTaskForm, LectureEditForm
from web.generators import generate_reset_password_code, generate_subscribe_code
from web.models import ResetCode, Message, Lecture, HomeWork, StartBox, Chat, UserModel, HomeWorkReview, \
    SubscribeTariff, Order, Code
from web.telegram_bot import send_message_in_telegram

load_dotenv()


def redirect_superuser(view_func):
    @wraps(view_func)
    def _wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return redirect(reverse("admin_dashboard"))
        if not request.user.is_authenticated:
            return redirect(reverse("login"))
        return view_func(request, *args, **kwargs)

    return _wrapper


def redirect_user(view_func):
    @wraps(view_func)
    def _wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_superuser:
            return redirect(reverse("dashboard"))
        if not request.user.is_authenticated:
            return redirect(reverse("login"))
        return view_func(request, *args, **kwargs)

    return _wrapper


def count_new_messages(user_chat_obj: Chat, user: UserModel) -> int | None:
    try:
        new_messages = Message.objects.filter(chat=user_chat_obj).filter(is_read_user=False).filter(
            ~Q(user_id=user.id)).count()
    except Chat.DoesNotExist:
        raise ValueError("Current user's chat was not found.")
    except Message.DoesNotExist:
        raise ValueError("Current user's message was not fount.")
    return new_messages if new_messages else None


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        try:
            tariff = self.request.POST.get("action")
            price = SubscribeTariff.objects.get(name=f"{tariff.lower()}")
            order = Order.objects.create(
                total_sum=Decimal(price.price),
            )

            checkout_session = stripe.checkout.Session.create(
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': f"Оплата за підписку '{price.name}' для \n Tanja Tattoo Academy"
                        },
                        'unit_amount': int(price.price * 100)
                    },
                    'quantity': 1
                }],
                mode='payment',
                success_url=request.build_absolute_uri(reverse("success_pay")),
                cancel_url=request.build_absolute_uri(reverse("cancel_pay")),
                metadata={"order_id": order.pk, "tariff": tariff}
            )
            response = HttpResponseRedirect(checkout_session.url)
            response.status_code = 303
            return response
        except Exception as e:
            print(e)
            return redirect(reverse("error_pay"))


@method_decorator(csrf_exempt, name="dispatch")
class Webhook(View):
    def post(self, request, *args, **kwargs):
        payload = request.body
        signature_header = request.headers.get("Stripe-Signature")
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        try:
            event = stripe.Webhook.construct_event(payload, signature_header, webhook_secret)
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            return HttpResponse(status=400)

        if event["type"] == "checkout.session.completed":
            try:
                order = Order.objects.get(pk=event["data"]["object"]["metadata"]["order_id"])
                email = event["data"]["object"]["customer_details"]["email"]
                session_id = event["data"]["object"]["id"]
                order.user_email = email
                order.session_id = session_id
                order.is_paid = True
                order.save()

                new_code = Code.objects.create(
                    code=generate_subscribe_code(),
                    order=order,
                    tariff=event["data"]["object"]["metadata"]["tariff"]
                )
                full_name = event["data"]["object"]["customer_details"]["name"]
                print("before", email, new_code.code, full_name)
            except Exception as e:
                print(f"Ошибка при обработке вебхука, но оплата прошла: {e}")
                return HttpResponse(status=500)
            else:
                print(email, new_code.code, full_name)
                send_email_subscribe_code(email=email, code=new_code.code, full_name=full_name)

        return HttpResponse(status=200)


class RegisterView(CreateView):
    form_class = CustomRegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy('login')

    def form_valid(self, form):
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

        chat_id = user.telegram_chat_id
        if chat_id:
            send_message_in_telegram(
                chat_id=chat_id,
                text=(
                    "✅ Ваш пароль було успішно змінено!\n"
                    "Тепер ви можете використовувати свій акаунт з новими даними.\n"
                    "Якщо це були не ви — негайно зверніться в підтримку. 🔒"
                )
            )

        return super().form_valid(form)


class IndexView(generic.FormView):
    template_name = "index.html"
    form_class = IndexForm
    success_url = reverse_lazy("answer")

    def get_context_data(self, **kwargs):
        user = self.request.user if self.request.user.is_authenticated else None
        context = super().get_context_data(**kwargs)

        context["user"] = user
        context["mentor"] = UserModel.objects.filter(is_superuser=True).first()
        return context

    def form_valid(self, form):
        name = form.cleaned_data.get("name", "")
        contact_method = form.cleaned_data.get("contact_method", "")
        contact_details = form.cleaned_data.get("contact_details", "")

        if name and contact_method and contact_details:
            mentor_chat_id = UserModel.objects.filter(is_superuser=True).first().telegram_chat_id
            if mentor_chat_id:
                send_message_in_telegram(
                    chat_id=mentor_chat_id,
                    text=(
                        "📩 Отримано нову форму зворотного зв'язку!\n\n"
                        f"👤 Ім'я: {name}\n"
                        f"🌐 Соцмережа: {contact_method}\n"
                        f"📞 Контакт: {contact_details}"
                    )
                )
        return super().form_valid(form)


@method_decorator(redirect_superuser, name="dispatch")
class DashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        chat, created = Chat.objects.get_or_create(user=user)
        new_sms = count_new_messages(user_chat_obj=chat, user=user)
        lectures_done_ids = HomeWorkReview.objects.filter(
            homework__user=user,
            homework__was_checked=True,
            is_approved=True
        ).values_list("homework__lecture_id", flat=True).distinct()
        lectures_count = Lecture.objects.count()

        next_lesson = Lecture.objects.filter(~Q(id__in=lectures_done_ids)).order_by("position_number").first()

        if lectures_count > 0:
            percent_done = int((len(lectures_done_ids) / lectures_count) * 100)
        else:
            percent_done = 0

        context["user"] = user
        context["chat_pk"] = get_object_or_404(Chat, user=user).pk
        context["new_sms"] = new_sms
        context["lesson"] = next_lesson
        context["percent_done"] = percent_done

        return context

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        user.last_activity = timezone.now()
        user.save()
        return super().dispatch(request, *args, **kwargs)


class ChatView(LoginRequiredMixin, generic.FormView):
    form_class = ChatForm
    template_name = "chat.html"

    def get_chat(self):
        user = self.request.user
        pk = self.kwargs.get("pk")

        if not pk and not user.is_superuser:
            chat = get_object_or_404(Chat, user=self.request.user)
            return chat

        chat = get_object_or_404(Chat, pk=pk)

        if chat.user == user or user.is_superuser:
            return chat

        raise PermissionDenied("Ви не маєте прав для перегляду цього чату.")

    def get_messages(self):
        chat = self.get_chat()
        return Message.objects.filter(chat=chat).order_by("date")

    def get_context_data(self, **kwargs):
        queryset = self.get_messages()

        paginator = Paginator(queryset, 20)
        page_obj = paginator.get_page(paginator.num_pages)
        queryset = page_obj.object_list

        user = self.request.user
        context = super().get_context_data(**kwargs)
        count_of_new_messages = Message.objects.filter(is_read_admin=False).count()
        count_of_waiting = HomeWork.objects.filter(was_checked=False).count()

        context["messages"] = queryset
        context["page_obj"] = page_obj
        if not user.is_superuser:
            chat_pk = get_object_or_404(Chat, user=user).pk
            context["interlocutor_avatar"] = UserModel.objects.filter(is_superuser=True).first().avatar.url

        if user.is_superuser:
            chat_pk = self.kwargs["pk"]
            context["interlocutor"] = Chat.objects.get(pk=chat_pk).user

        context["chat_pk"] = chat_pk
        context["user"] = self.request.user

        context["admin_ids"] = UserModel.objects.filter(is_superuser=True).values_list("id", flat=True)

        context["count_of_new_messages"] = count_of_new_messages
        context["count_of_waiting"] = count_of_waiting

        return context

    def form_valid(self, form):
        message = form.save(commit=False)
        message.chat = self.get_chat()
        message.user = self.request.user
        if self.request.user.is_superuser:
            message.is_read_admin = True
            message.from_admin = True
            user_chat_id = message.chat.user.telegram_chat_id
            if user_chat_id:
                send_message_in_telegram(chat_id=user_chat_id,
                                         text="🧑‍🏫 Ментор щойно надіслав вам повідомлення. Загляньте в особистий кабінет 😊")
        else:
            message.is_read_user = True
            mentor_chat_id = UserModel.objects.filter(is_superuser=True).first().telegram_chat_id
            if mentor_chat_id:
                send_message_in_telegram(chat_id=mentor_chat_id, text=(
                    f"🧑‍🎓 Учень {message.user.get_full_name()} надіслав повідомлення!\n\n"
                    f"📝 \"{message.text}\"\n\n"
                    f"🔗 Відкрийте чат на платформі, щоб відповісти."
                ))
        message.save()

        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return redirect("login")

        if user.is_superuser:
            pk = self.kwargs["pk"]
            chat = Chat.objects.get(pk=pk)
            Message.objects.filter(chat=chat).filter(is_read_admin=False).update(is_read_admin=True)
        elif not user.is_superuser:
            chat = Chat.objects.get(user=user)
            Message.objects.filter(chat=chat).filter(is_read_user=False).update(is_read_user=True)
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        if self.request.user.is_superuser:
            return ["chat-admin.html"]
        return ["chat.html"]

    def get_success_url(self):
        chat_id = self.kwargs["pk"]
        return reverse("chat", args=[chat_id])


def get_part_of_messages(request, pk):
    try:
        chat = get_object_or_404(Chat, pk=pk)
        messages = Message.objects.filter(chat=chat).order_by("date")
        paginator = Paginator(messages, 20)
        current_page = request.GET.get("page", None)
        page_obj = paginator.get_page(current_page)
        messages = page_obj.object_list

        html = render_to_string("partial/_messages_partial.html", {"messages": messages, "user": request.user})
        return HttpResponse(html)
    except Exception as e:
        print(e)
        return HttpResponseServerError


@method_decorator(redirect_superuser, name="dispatch")
class ProfileUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "profile.html"
    model = UserModel
    form_class = ProfileForm
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["user"] = user

        if not user.is_superuser:
            chat = Chat.objects.filter(user=user).first()
            if chat:
                new_sms = count_new_messages(user_chat_obj=chat, user=user)
                context["new_sms"] = new_sms
                context["chat_pk"] = chat.pk

        return context

    def form_valid(self, form):
        is_password_change = 'change_password' in self.request.POST

        if is_password_change:
            new_password = form.cleaned_data.get('new_password1')
            if new_password:
                form.instance.set_password(new_password)
                messages.success(self.request, "Ваш пароль було успішно змінено!")
                update_session_auth_hash(self.request, form.instance)
        else:
            if 'avatar' in form.changed_data:
                old_user_instance = self.get_object()
                old_avatar = old_user_instance.avatar
                if old_avatar and "base_icon.png" not in old_avatar.name:
                    if os.path.exists(old_avatar.path):
                        old_avatar.delete(save=False)

            messages.success(self.request, "Ваші дані було успішно оновлено.")

        return super().form_valid(form)


@method_decorator(redirect_superuser, name="dispatch")
class CourseView(LoginRequiredMixin, generic.FormView):
    template_name = "course.html"
    model = Lecture
    form_class = LectureHomeworkUserForm

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        chat = get_object_or_404(Chat, user=user)
        lectures = Lecture.objects.order_by("position_number")
        new_sms = count_new_messages(user_chat_obj=chat, user=user)

        homework_review_count = HomeWorkReview.objects.filter(
            homework__user=user,
            homework__was_checked=True,
            is_approved=True
        ).count()
        paginator = Paginator(lectures, 10)
        current_page = self.request.GET.get("page")
        context["page_obj"] = paginator.get_page(current_page)

        homework_done_posit_nums = HomeWorkReview.objects.filter(homework__user=user, homework__was_checked=True,
                                                                 is_approved=True).values_list(
            "homework__lecture__position_number", flat=True
        )
        current_task = lectures.filter(~Q(position_number__in=homework_done_posit_nums)).first()

        context["homework_done_ids"] = homework_done_posit_nums
        context["request"] = self.request

        context["new_sms"] = new_sms
        context["homework_review_count"] = homework_review_count
        context["current_task"] = current_task.position_number or (
            None if homework_review_count == lectures.count() else 1)
        context["chat_pk"] = chat.pk
        context["current_id"] = self.kwargs["pk"] if self.kwargs["pk"] else 1
        context["user_tasks_waiting_for_review_pos_nums"] = HomeWork.objects.filter(user=user,
                                                                                    was_checked=False).values_list(
            "lecture__position_number", flat=True)

        position_number = self.kwargs.get("pk")
        if position_number:
            try:
                lecture_data = lectures.get(position_number=position_number)
                context["lecture"] = lecture_data
            except Lecture.DoesNotExist:
                raise Http404("Такої лекції немає")
            else:
                homework = HomeWork.objects.filter(user=user, lecture__position_number=position_number).first()
                if homework and homework.lecture.position_number in homework_done_posit_nums:
                    context["homework_text"] = homework.text

        return context

    def get(self, request, *args, **kwargs):
        per_page = 10

        current_lecture_pk = int(self.kwargs["pk"])
        page_from_request = request.GET.get("page")
        user = self.request.user
        count_of_done_homework = HomeWorkReview.objects.filter(homework__user=user, is_approved=True,
                                                               homework__was_checked=True).count()

        if not page_from_request:
            try:
                lecture = Lecture.objects.get(position_number=current_lecture_pk)
            except Lecture.DoesNotExist:
                raise Http404("Такої лекції немає.")

            position = Lecture.objects.filter(position_number__lt=lecture.position_number).count()
            correct_page = position // per_page + 1

            url = reverse("course", kwargs={"pk": current_lecture_pk})
            return HttpResponseRedirect(f"{url}?page={correct_page}")

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):

        text = form.cleaned_data.get("text", "")
        image = form.cleaned_data.get("image", "")
        user = self.request.user
        lecture_positional_number = self.kwargs.get("pk", "")

        if lecture_positional_number:
            lecture_obj = get_object_or_404(Lecture, position_number=int(lecture_positional_number))
        if not lecture_positional_number:
            return HttpResponseRedirect(reverse("course", kwargs={"pk": 1}))
        if not text and not image:
            return HttpResponseRedirect(reverse("course", kwargs={"pk": int(lecture_positional_number)}))

        homework = HomeWork.objects.create(
            lecture=lecture_obj,
            user=user,
            image=image if image else None,
            text=text if text else None
        )
        user_chat_id = user.telegram_chat_id
        if user_chat_id:
            send_message_in_telegram(chat_id=user_chat_id, text=(
                "📨 Ми отримали ваше домашнє завдання!\n"
                "Очікуйте на перевірку від ментора — щойно він її завершить, я одразу вам напишу 😉"
            ))
        mentor_chat_id = UserModel.objects.filter(is_superuser=True).first().telegram_chat_id
        if mentor_chat_id:
            send_message_in_telegram(chat_id=mentor_chat_id, text=(
                f"📬 Учень {user.get_full_name()} щойно надіслав домашнє завдання для уроку «{lecture_obj.lecture_name}».\n"
                "Перевірте, будь ласка, його в особистому кабінеті."
            ))

        return super().form_valid(form)

    def get_success_url(self):
        pk = int(self.kwargs.get("pk"))
        try:
            next_lecture = Lecture.objects.filter(position_number__gt=pk).order_by("position_number").first()
            if next_lecture:
                return reverse("course", kwargs={"pk": next_lecture.position_number})
        except Exception as e:
            print(e)
            return reverse("course", kwargs={"pk": 1})


@method_decorator(redirect_superuser, name="dispatch")
class BoxApplicationView(LoginRequiredMixin, generic.FormView):
    template_name = "box-application.html"
    model = StartBox
    form_class = BoxApplicationForm
    success_url = reverse_lazy("box_application")

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)

        context["tariff"] = user.code.tariff
        context["user"] = user
        context["start_box"] = StartBox.objects.get(user=user) if user.code.start_box_coupon_is_activated else None

        if StartBox.objects.filter(user=user) and user.code.tariff != "base":
            context[
                "sms"] = "Ви вже заповнили цю форму. Ви можете отримати StartBox лише один раз. Якщо ви її заповнили недавно то очікуйте смс від пошти. Ми відправимо вам бокс як можна швидше."
        elif not StartBox.objects.filter(user=user) and user.code.tariff != "base":
            context["sms"] = "Заповніть анкету нижче, і ми відправимо вам набір з усім необхідним для початку роботи."
        elif user.code.tariff == "base":
            context[
                "sms"] = "Нажаль ваш тариф не включає стартовий бокс але ви можете звернутися до ментора в чаті якщо захотіли придбати."

        if not user.is_superuser:
            chat = get_object_or_404(Chat, user=user)
            new_sms = count_new_messages(user_chat_obj=chat, user=user)
            context["new_sms"] = new_sms
            context["chat_pk"] = chat.pk

        return context

    def form_valid(self, form):
        if self.request.user.code.tariff != "base":
            with transaction.atomic():
                if not self.request.user.code.start_box_coupon_is_activated:
                    full_name = form.cleaned_data.get("full_name", "")
                    phone = form.cleaned_data.get("phone", "")
                    address = form.cleaned_data.get("address", "")
                    comments = form.cleaned_data.get("comments", "")

                    user = self.request.user

                    StartBox.objects.create(
                        full_name=full_name,
                        phone=phone,
                        address=address,
                        comments=comments,
                        user=user
                    )

                    code = user.code
                    code.start_box_coupon_is_activated = True
                    code.save()

                    user_chat_id = user.telegram_chat_id
                    if user_chat_id:
                        send_message_in_telegram(
                            chat_id=user_chat_id,
                            text=(
                                "📨 Ми отримали вашу заявку на тату-бокс!\n"
                                "Як тільки відправлення буде здійснено — я повідомлю вас у цей чат. Дякуємо за довіру! 🧡"
                            )
                        )

                    mentor_chat_id = UserModel.objects.filter(is_superuser=True).first().telegram_chat_id
                    if mentor_chat_id:
                        send_message_in_telegram(
                            chat_id=mentor_chat_id,
                            text=(
                                f"📬 Учень {user.get_full_name()} щойно надіслав анкету на тату-бокс.\n"
                                "Перевірте, будь ласка, нову заявку у кабінеті."
                            )
                        )

                    return redirect(f"{reverse(f'box_application')}?success=true")

        return redirect("box_application")


@method_decorator(redirect_user, name="dispatch")
class AdminReviewListView(LoginRequiredMixin, generic.ListView):
    template_name = "admin-review-list.html"
    model = HomeWork
    context_object_name = "homeworks"

    def get_queryset(self):
        queryset = super().get_queryset()
        query_param = self.request.GET.get("type")
        if query_param == "waiting_for_a_check":
            return queryset.filter(was_checked=False).select_related("lecture", "user")

        elif query_param == "approved":
            approved_hw_ids = HomeWorkReview.objects.filter(is_approved=True).values_list("homework_id", flat=True)
            return queryset.filter(was_checked=True, id__in=approved_hw_ids).select_related("lecture", "user")

        else:
            return queryset.select_related("lecture", "user")

    def get_context_data(
            self, *, object_list=..., **kwargs
    ):
        context = super().get_context_data(**kwargs)
        approved_ids = HomeWorkReview.objects.filter(is_approved=True).values_list("homework_id", flat=True)
        count_of_new_messages = Message.objects.filter(is_read_admin=False).count()
        count_of_waiting = HomeWork.objects.filter(was_checked=False).count()
        approved = HomeWork.objects.filter(was_checked=True, id__in=approved_ids).count()
        all_ = HomeWork.objects.count()

        context["type"] = self.request.GET.get("type")
        context["count_of_waiting"] = count_of_waiting
        context["count_of_approved"] = approved
        context["all"] = all_
        context["count_of_new_messages"] = count_of_new_messages

        return context


@method_decorator(redirect_user, name="dispatch")
class AdminReviewTaskView(LoginRequiredMixin, generic.FormView):
    template_name = "admin-review-task.html"
    model = HomeWork
    form_class = ReviewTaskForm

    def form_valid(self, form):
        with transaction.atomic():
            review_text = form.cleaned_data.get("review_text", "(немає коментаря).")
            pk = self.kwargs.get("pk")
            homework = get_object_or_404(HomeWork, pk=pk)

            action = self.request.POST.get("action")
            if action == "reject" and not review_text:
                messages.error(self.request, "Будь ласка, напишіть коментар, чому робота відхилена.")
                return self.form_invalid(form)

            HomeWorkReview.objects.create(
                homework=homework,
                review_text=review_text,
                is_approved=True if action == "approve" else False,
            )

            homework.was_checked = True
            homework.save()

            chat = homework.user.chats
            if chat:
                user_chat_id = homework.user.telegram_chat_id
                if action == "approve":
                    Message.objects.create(
                        chat=chat,
                        text=f"✅ Ваше завдання було прийняте ментором! 🎉      💬 Коментар ментора: {review_text if review_text else '(немає коментаря)'}",
                        user=self.request.user,
                        is_read_admin=True,
                        from_admin=True
                    )
                    if user_chat_id:
                        send_message_in_telegram(chat_id=user_chat_id,
                                                 text="✅ Ваше завдання було прийняте ментором! 🎉\n Для перегляду деталей перейдіть на платформу.🧡")
                else:
                    Message.objects.create(
                        chat=chat,
                        text=f"❌ На жаль, завдання не було прийняте ментором. 😔     💬 Коментар ментора: '{review_text}' P.S: Не засмучуйтесь, спробуйте ще раз — у вас все вийде! 💪",
                        user=self.request.user,
                        is_read_admin=True,
                        from_admin=True
                    )
                    if user_chat_id:
                        send_message_in_telegram(chat_id=user_chat_id,
                                                 text="❌ На жаль, завдання не було прийняте ментором. 😔\n Для перегляду деталей перейдіть на платформу.🧡")

            return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.kwargs.get("pk")
        count_of_new_messages = Message.objects.filter(is_read_admin=False).count()
        count_of_waiting = HomeWork.objects.filter(was_checked=False).count()
        if pk:
            try:
                homework = HomeWork.objects.get(pk=pk)
                context["homework"] = homework
            except HomeWork.DoesNotExist:
                return reverse("admin_review_list") + "?type=waiting_for_a_check"

        context["count_of_new_messages"] = count_of_new_messages
        context["count_of_waiting"] = count_of_waiting

        return context

    def get_success_url(self):
        return reverse("admin_review_list") + "?type=waiting_for_a_check"


@method_decorator(redirect_user, name="dispatch")
class AdminDashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = "admin-dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        count_of_waiting = HomeWork.objects.filter(was_checked=False).count()
        count_of_new_messages = Message.objects.filter(is_read_admin=False).count()
        waiting_for_check = HomeWork.objects.filter(was_checked=False).select_related("lecture", "user").order_by(
            "-date")[:3]

        latest_ids = (
            Message.objects.values("chat_id").filter(is_read_admin=False).annotate(latest_id=Max("id")).values_list(
                "latest_id", flat=True)
        )

        last_messages = Message.objects.filter(id__in=latest_ids).select_related("user").order_by("-date")
        lectures_count = Lecture.objects.count()

        query_counting = HomeWorkReview.objects.filter(
            homework__user_id=OuterRef("pk"),
            is_approved=True
        ).select_related("homework__user").values("homework__user_id").annotate(
            c=Count("id")
        ).values("c")

        users_with_progress = UserModel.objects.filter(is_superuser=False).annotate(
            progress=(
                    Cast(Subquery(query_counting), IntegerField()) * 100 / lectures_count
            )
        )

        min_user_progress = users_with_progress.order_by("progress").first()

        max_user_progress = users_with_progress.order_by("-progress").first()

        context["count_of_waiting"] = count_of_waiting
        context["waiting_for_check"] = waiting_for_check
        context["count_of_new_messages"] = count_of_new_messages
        context["last_messages"] = last_messages
        context["min_progress"] = min_user_progress
        context["max_progress"] = max_user_progress

        return context


@method_decorator(redirect_user, name="dispatch")
class AdminStudentsView(LoginRequiredMixin, generic.ListView):
    template_name = "admin-students.html"
    model = UserModel
    context_object_name = "users"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        count_of_waiting = HomeWork.objects.filter(was_checked=False).count()
        count_of_new_messages = Message.objects.filter(is_read_admin=False).count()

        context["count_of_waiting"] = count_of_waiting
        context["count_of_new_messages"] = count_of_new_messages

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        all_lectures = Lecture.objects.count()
        search_query = self.request.GET.get("q")
        progres_query = self.request.GET.get("progress")

        homeworks_done_counter_query = HomeWorkReview.objects.filter(
            homework__user_id=OuterRef("pk"),
            is_approved=True
        ).values("homework__user_id").annotate(c=Count("id")).values("c")

        queryset = queryset.filter(is_superuser=False).annotate(
            progress=Cast(Subquery(homeworks_done_counter_query), FloatField()) * 100 / all_lectures
        )

        if search_query:
            queryset = queryset.filter(Q(email__icontains=search_query) | Q(first_name__icontains=search_query) | Q(
                last_name__icontains=search_query))

        if progres_query:
            if progres_query == "low":
                queryset = queryset.filter(Q(progress__lte=30) | Q(progress=None))
            if progres_query == "medium":
                queryset = queryset.filter(progress__gte=30).filter(progress__lte=80)
            if progres_query == "high":
                queryset = queryset.filter(progress__gte=80)

        return queryset.select_related("chats", "code")


@method_decorator(redirect_user, name="dispatch")
class AdminBoxesView(LoginRequiredMixin, generic.ListView):
    template_name = "admin-boxes.html"
    model = StartBox
    context_object_name = "boxes"
    paginate_by = 16

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.GET.get("type") == "active":
            return queryset.filter(is_sent=False).select_related("user")
        elif self.request.GET.get("type") == "sent":
            return queryset.filter(is_sent=True).select_related("user")
        return queryset.select_related("user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        count_of_waiting = HomeWork.objects.filter(was_checked=False).count()
        count_of_new_messages = Message.objects.filter(is_read_admin=False).count()

        context["count_of_new_messages"] = count_of_new_messages
        context["count_of_waiting"] = count_of_waiting
        context["filter"] = self.request.GET.get("type")
        context["active_count"] = StartBox.objects.filter(is_sent=False).count()
        context["sent_count"] = StartBox.objects.filter(is_sent=True).count()

        return context

    def post(self, request, *args, **kwargs):
        box_id = self.request.POST.get("mark_as_sent")
        with transaction.atomic():
            if box_id:
                try:
                    box = StartBox.objects.get(pk=box_id)
                    box.is_sent = True
                    box.sent_date = timezone.now()
                    box.save()
                    chat = Chat.objects.get(user=box.user)
                except StartBox.DoesNotExist:
                    raise Http404("Старт боксу не існує...")
                else:
                    Message.objects.create(
                        chat=chat,
                        text="📦 Привіт! Ми відправили твій Start Box з тату-приладдям 🖋️🚚 Посилка вже в дорозі до тебе за вказаною адресою!",
                        user=box.user,
                        is_read_admin=True,
                        from_admin=True
                    )
                    user = self.request.user
                    if user and user.telegram_chat_id:
                        send_message_in_telegram(chat_id=user.telegram_chat_id,
                                                 text="📦 Привіт! Ми відправили твій Start Box з тату-приладдям 🖋️🚚\n Посилка вже в дорозі до тебе за вказаною адресою!")

        return HttpResponseRedirect(reverse("admin_boxes") + "?type=active")


@method_decorator(redirect_user, name="dispatch")
class AdminLectureList(LoginRequiredMixin, generic.ListView):
    template_name = "admin-lecture-list.html"
    model = Lecture
    context_object_name = "lectures"
    queryset = Lecture.objects.order_by("position_number")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        count_of_waiting = HomeWork.objects.filter(was_checked=False).count()
        count_of_new_messages = Message.objects.filter(is_read_admin=False).count()

        context["count_of_waiting"] = count_of_waiting
        context["count_of_new_messages"] = count_of_new_messages

        return context

    def post(self, request, *args, **kwargs):
        if "delete" in request.POST:
            Lecture.objects.get(pk=request.POST.get("pk")).delete()
            return redirect("admin_lecture_list")
        return super().get(request, *args, **kwargs)


@method_decorator(redirect_user, name="dispatch")
class AdminLectureCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "admin-lecture-create.html"
    model = Lecture
    form_class = LectureEditForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        position_number = Lecture.objects.values_list("position_number", flat=True)
        count_of_waiting = HomeWork.objects.filter(was_checked=False).count()
        count_of_new_messages = Message.objects.filter(is_read_admin=False).count()

        context["count_of_waiting"] = count_of_waiting
        context["position_number"] = max(position_number) + 1
        context["count_of_new_messages"] = count_of_new_messages

        return context

    def get_initial(self):
        initial = super().get_initial()
        last_position_number = int(Lecture.objects.aggregate(max_position=Max("position_number"))["max_position"] or 1)
        initial["position_number"] = last_position_number + 1
        return initial

    def get_success_url(self):
        return reverse("admin_lecture_list")


@method_decorator(redirect_user, name="dispatch")
class AdminLectureEditView(LoginRequiredMixin, generic.UpdateView):
    template_name = "admin-lecture-edit.html"
    model = Lecture
    context_object_name = "lecture"
    form_class = LectureEditForm
    success_url = reverse_lazy("admin_lecture_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        count_of_waiting = HomeWork.objects.filter(was_checked=False).count()
        count_of_new_messages = Message.objects.filter(is_read_admin=False).count()

        context["count_of_waiting"] = count_of_waiting
        context["count_of_new_messages"] = count_of_new_messages

        return context


@method_decorator(redirect_user, name="dispatch")
class AdminLectureDelete(LoginRequiredMixin, generic.DeleteView):
    model = Lecture
    template_name = "admin_lecture_delete.html"

    def get_success_url(self):
        return reverse("admin_lecture_list")


@method_decorator(redirect_user, name="dispatch")
class AdminAllChatsView(LoginRequiredMixin, generic.ListView):
    template_name = "admin-all-chats.html"
    model = Chat
    context_object_name = "chats"
    paginate_by = 30

    def get_queryset(self):
        subquery_get_last_message = Message.objects.filter(
            chat=OuterRef("pk"),
        ).order_by("-id").values("text")[:1][:15]

        queryset = Chat.objects.annotate(
            message_count=Count(
                'messages',
                filter=Q(messages__is_read_admin=False)
            ),
            last_message_date=Max("messages__date"),
            last_message=Subquery(subquery_get_last_message)
        ).order_by('-message_count', '-last_message_date').select_related("user")

        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q) | Q(user__email__icontains=q))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        count_of_waiting = HomeWork.objects.filter(was_checked=False).count()
        count_of_new_messages = Message.objects.filter(is_read_admin=False).count()

        context["count_of_waiting"] = count_of_waiting
        context["count_of_new_messages"] = count_of_new_messages

        return context
