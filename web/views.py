import json
from datetime import timedelta
from functools import wraps

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Max, OuterRef, Subquery, FloatField
from django.db.models.functions import Cast
from django.forms import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import localtime
from django.views import generic
from django.views.generic import CreateView

from web.email_sender import send_password_change_email, send_after_register_email
from web.forms import CustomRegisterForm, PasswordChangeRequestForm, ChangePasswordForm, BoxApplicationForm, \
    ProfileForm, ChatForm, IndexForm, LectureHomeworkUserForm, ReviewTaskForm, LectureEditForm, LectureCreateForm
from web.generators import generate_reset_password_code
from web.models import ResetCode, Message, Lecture, HomeWork, StartBox, Chat, UserModel, HomeWorkReview


def redirect_superuser(view_func):
    wraps(view_func)
    def _wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return redirect("/platform/admin_dashboard")
        return view_func(request, *args, **kwargs)
    return _wrapper

def redirect_user(view_func):
    wraps(view_func)
    def _wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_superuser:
            return redirect("/platform/dashboard/")
        return view_func(request, *args, **kwargs)
    return _wrapper


def count_new_messages(user_chat_obj: Chat, user: UserModel) -> int | None:
    try:
        new_messages = Message.objects.filter(chat=user_chat_obj).filter(is_read_user=False).filter(~Q(user_id=user.id)).count()
    except Chat.DoesNotExist:
        raise ValueError("Current user's chat was not found.")
    except Message.DoesNotExist:
        raise ValueError("Current user's message was not fount.")
    return new_messages if new_messages else None


class RegisterView(CreateView):
    form_class = CustomRegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        code_obj = form.cleaned_data.get("code", None)
        if code_obj:
            code_obj.is_activated = True
            code_obj.activated_date = timezone.now()
            code_obj.save()

            Chat.objects.create(
                user=self.request.user
            )

        email = form.cleaned_data.get("email", "")
        full_name = form.cleaned_data.get("first_name", "") + " " + form.cleaned_data.get("last_name", "")
        if email and full_name:
            send_after_register_email(email=email, full_name=full_name)

        self.object = form.save()
        return super().form_valid(form)


class ChangePasswordRequestView(generic.FormView):
    form_class = PasswordChangeRequestForm
    template_name = "registration/change_password_request.html"
    success_url = reverse_lazy("email_sent_info")

    def form_valid(self, form):
        if form.cleaned_data["email"] is not None and form.cleaned_data["full_name"] is not None:
            email = form.cleaned_data["email"]
            full_name = form.cleaned_data["full_name"]
            code = generate_reset_password_code()
            ResetCode.objects.create(
                user_email=email,
                code=code,
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
        code = form.cleaned_data.get("code", "")
        password = form.cleaned_data.get("password1", "")

        if password and code:
            try:
                code_obj = ResetCode.objects.get(code=code)
                if code_obj.is_activated is True:
                    raise ValueError("Нажаль ваш код вже активований.")

                if code_obj.created_date + timedelta(minutes=15) < timezone.now():
                    raise ValueError("Нажаль ваш код прострочений.")

                user = get_user_model().objects.get(email=code_obj.user_email)

                if user:
                    user.set_password(password)
                    user.save()
                return super().form_valid(form)

            except get_user_model().DoesNotExist:
                raise ValueError("Користувача з таким email немає")

        else:
            raise ValueError("Неправильний код або пароль.")


class IndexView(generic.FormView):
    template_name = "index.html"
    form_class = IndexForm
    success_url = reverse_lazy("index")

    def get_context_data(self, **kwargs):
        user = self.request.user if self.request.user.is_authenticated else None
        context = super().get_context_data(**kwargs)

        context["user"] = user
        return context


@method_decorator(redirect_superuser, name="dispatch")
class DashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        if not user.is_superuser:
            chat = Chat.objects.get(user=user)
            new_sms = count_new_messages(user_chat_obj=chat, user=user)
            next_lesson = HomeWorkReview.objects.filter(
                homework__user=user,
                homework__was_checked=True,
                is_approved=True
            ).count() + 1

            if Lecture.objects.count() >= next_lesson:
                lesson = Lecture.objects.get(position_number=next_lesson)
            else:
                lesson = None

            lectures_count = Lecture.objects.count()

        context["user"] = user
        context["chat_pk"] = get_object_or_404(Chat, user=user).pk
        context["new_sms"] = new_sms
        context["lesson"] = lesson
        context["next_lesson"] = next_lesson
        context["percent_done"] = int(((next_lesson - 1) / lectures_count) * 100)

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

        try:
            if user.is_superuser:
                pk = self.kwargs["pk"]
                return Chat.objects.get(pk=pk)
            elif not user.is_superuser:
                return Chat.objects.get(user=user)
        except Chat.DoesNotExist:
            raise ValueError("Current user's chat was not found.")

    def get_messages(self):
        chat = self.get_chat()
        return Message.objects.filter(chat=chat).order_by("date")

    def get_context_data(self, **kwargs):
        queryset = self.get_messages()
        user = self.request.user
        context = super().get_context_data(**kwargs)
        count_of_new_messages = Message.objects.filter(is_read_admin=False).count()
        count_of_waiting = HomeWork.objects.filter(was_checked=False).count()

        messages = []
        for message in queryset:
            message_dict = model_to_dict(message)
            message_dict["send_time"] = localtime(message.date).strftime("%H:%M")
            messages.append(message_dict)

        context["messages"] = messages
        if not user.is_superuser:
            chat_pk = get_object_or_404(Chat, user=user).pk
            context["interlocutor_avatar"] = UserModel.objects.filter(is_superuser=True).first().avatar.url

        if user.is_superuser:
            chat_pk = self.kwargs["pk"]
            context["interlocutor_avatar"] = Chat.objects.get(pk=chat_pk).user.avatar.url

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
        else:
            message.is_read_user = True
        message.save()

        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_superuser:
            pk=self.kwargs["pk"]
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

@method_decorator(redirect_superuser, name="dispatch")
class ProfileView(LoginRequiredMixin, generic.FormView):
    template_name = "profile.html"
    model = get_user_model()
    form_class = ProfileForm
    success_url = reverse_lazy("profile")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        context["user"] = user

        if not user.is_superuser:
            chat = Chat.objects.get(user=user)
            new_sms = count_new_messages(user_chat_obj=chat, user=user)
            context["new_sms"] = new_sms
            context["chat_pk"] = get_object_or_404(Chat, user=user).pk

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        user = self.request.user
        password = getattr(user, "password", None)

        if not password:
            raise ValueError("User has no password set")

        kwargs["hashed_current_password"] = password
        kwargs["user_id"] = user.id
        print(user.password)
        return kwargs


    def form_valid(self, form):
        new_password = form.cleaned_data.get("new_password", "")
        first_name = form.cleaned_data.get("first_name", "")
        last_name = form.cleaned_data.get("last_name", "")
        email = form.cleaned_data.get("email", "")
        phone = form.cleaned_data.get("phone", "")
        avatar = form.cleaned_data.get("avatar", "")

        user = self.request.user
        if new_password:
            user.set_password(new_password)
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email
        if phone:
            user.phone = phone
        if avatar:
            user.avatar = avatar

        user.save()

        return super().form_valid(form)


@method_decorator(redirect_superuser, name="dispatch")
class CourseView(LoginRequiredMixin, generic.FormView):
    template_name = "course.html"
    model = Lecture
    form_class = LectureHomeworkUserForm

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        if not user.is_superuser:
            chat = Chat.objects.get(user=user)
            new_sms = count_new_messages(user_chat_obj=chat, user=user)
            context["new_sms"] = new_sms
        lectures = Lecture.objects.all().order_by("position_number")
        context["lectures"] = lectures
        homework_review_count = HomeWorkReview.objects.filter(
            homework__user=user,
            homework__was_checked=True,
            is_approved=True
        ).count()
        context["homework_review_count"] = homework_review_count
        context["homework_review_count_plus_1"] = homework_review_count + 1
        context["chat_pk"] = get_object_or_404(Chat, user=user).pk
        context["current_id"] = self.kwargs["pk"] if self.kwargs["pk"] else 1

        pk = self.kwargs.get("pk")
        if pk:
            try:
                lecture_data = Lecture.objects.get(pk=pk)
                context["lecture"] = lecture_data
            except Exception:
                raise Lecture.DoesNotExist

        return context

    def form_valid(self, form):
        text = form.cleaned_data.get("text", "")
        image = form.cleaned_data.get("image", "")
        user = self.request.user
        lecture_pk = self.kwargs.get("pk", "")
        lecture_obj = Lecture.objects.get(pk=lecture_pk)

        if not text and image:
            return reverse("course", kwargs={"pk": 1})

        homework = HomeWork.objects.create(
            lecture=lecture_obj,
            user=user,
            image=image if image else None,
            text=text if text else None
        )

        return super().form_valid(form)

    def get_success_url(self):
        pk = self.kwargs["pk"]
        if pk and Lecture.objects.filter(pk=pk).exists():
            return reverse("course", kwargs={"pk": pk + 1})
        return reverse("course", kwargs={"pk": 1})

@method_decorator(redirect_superuser, name="dispatch")
class BoxApplicationView(LoginRequiredMixin, generic.FormView):
    template_name = "box-application.html"
    model = StartBox
    form_class = BoxApplicationForm

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)

        context["tariff"] = user.code.tariff
        context["user"] = user

        if StartBox.objects.filter(user=user) and user.code.tariff != "base":
            context["sms"] = "Ви вже заповнили цю форму. Ви можете отримати StartBox лише один раз. Якщо ви її заповнили недавно то очікуйте смс від пошти. Ми відправимо вам бокс як можна швидше."
        elif not StartBox.objects.filter(user=user) and user.code.tariff != "base":
            context["sms"] = "Заповніть анкету нижче, і ми відправимо вам набір з усім необхідним для початку роботи."
        elif user.code.tariff == "base":
            context["sms"] = "Нажаль ваш тариф не включає стартовий бокс але ви можете звернутися до ментора в чаті якщо захотіли придбати."

        if not user.is_superuser:
            chat = Chat.objects.get(user=user)
            new_sms = count_new_messages(user_chat_obj=chat, user=user)
            context["new_sms"] = new_sms
            context["chat_pk"] = get_object_or_404(Chat, user=user).pk

        return context


    def form_valid(self, form):
        if self.request.user.code.tariff != "base" and self.request.user.code.start_box_coupon_is_activated is False:
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

            user.code.start_box_coupon_is_activated = True
            return super().form_valid(form)
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
            return queryset.filter(was_checked=False)

        elif query_param == "approved":
            queryset = queryset.filter(was_checked=True)
            approved_hw_ids = HomeWorkReview.objects.filter(is_approved=True).values_list("homework_id", flat=True)
            return queryset.filter(was_checked=True, id__in=approved_hw_ids)

        else:
            return queryset

    def get_context_data(
        self, *, object_list = ..., **kwargs
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
        review_text = form.cleaned_data.get("review_text")
        pk = self.kwargs.get("pk")
        homework = HomeWork.objects.get(pk=pk)

        action = self.request.POST.get("action")

        HomeWorkReview.objects.create(
            homework=homework,
            review_text=review_text,
            is_approved=True if action == "approve" else False,
        )

        homework.was_checked = True
        homework.save()

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

        context["count_of_waiting"] = count_of_waiting
        context["count_of_new_messages"] = count_of_new_messages

        return context


@method_decorator(redirect_user, name="dispatch")
class AdminStudentsView(LoginRequiredMixin, generic.ListView):
    template_name = "admin-students.html"
    model = UserModel
    context_object_name = "users"

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
            queryset = queryset.filter(Q(email__icontains=search_query) | Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query))

        if progres_query:
            if progres_query == "low":
                queryset = queryset.filter(Q(progress__lte=30) | Q(progress=None))
            if progres_query == "medium":
                queryset = queryset.filter(progress__gte=30).filter(progress__lte=80)
            if progres_query == "high":
                queryset = queryset.filter(progress__gte=80)

        return queryset

@method_decorator(redirect_user, name="dispatch")
class AdminBoxesView(LoginRequiredMixin, generic.ListView):
    template_name = "admin-boxes.html"
    model = StartBox
    context_object_name = "boxes"

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.GET.get("type") == "active":
            return queryset.filter(is_sent=False)
        elif self.request.GET.get("type") == "sent":
            return queryset.filter(is_sent=True)

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
        if box_id:
            try:
                box = StartBox.objects.get(pk=box_id)
                box.is_sent = True
                box.sent_date = timezone.now()
                box.save()
            except StartBox.DoesNotExist:
                pass

        return HttpResponseRedirect(reverse("admin_boxes") + "?type=active")


@method_decorator(redirect_user, name="dispatch")
class AdminLectureList(LoginRequiredMixin, generic.ListView):
    template_name = "admin-lecture-list.html"
    model = Lecture
    context_object_name = "lectures"

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

    def get_success_url(self):
        return reverse("admin_lecture_list")


@method_decorator(redirect_user, name="dispatch")
class AdminLectureEditView(LoginRequiredMixin, generic.UpdateView):
    template_name = "admin-lecture-edit.html"
    model = Lecture


class AdminAllChatsView(LoginRequiredMixin, generic.ListView):
    template_name = "admin-all-chats.html"
    model = Chat
