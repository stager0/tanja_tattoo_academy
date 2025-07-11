from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.views.generic import CreateView

from web.email_sender import send_password_change_email, send_after_register_email
from web.forms import CustomRegisterForm, PasswordChangeRequestForm, ChangePasswordForm
from web.generators import generate_reset_password_code
from web.models import ResetCode, Message, Lecture, HomeWork, StartBox


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


class DashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        try:
            chat = Chat.objects.get(user=user)
            new_sms = Message.objects.filter(chat=chat).count()
        except Chat.DoesNotExist:
            raise ValueError("Current user's chat was not found.")
        except Message.DoesNotExist:
            raise ValueError("Current user's message was not fount.")

        context["user"] = user
        context["new_sms"] = new_sms

        return context


class ChatView(LoginRequiredMixin, generic.FormView):
    form_class = ChatForm
    template_name = "chat.html"
    success_url = reverse_lazy("chat")

    def get_chat(self):
        user = self.request.user
        try:
            return Chat.objects.get(user=user)
        except Chat.DoesNotExist:
            raise ValueError("Current user's chat was not found.")

    def get_messages(self):
        chat = self.get_chat()
        return Message.objects.filter(chat=chat).order_by("date")

    def get_context_data(self, **kwargs):
        queryset = self.get_messages()
        context = super().get_context_data(**kwargs)

        messages = []
        for message in queryset:
            message_dict = model_to_dict(message)
            message_dict["send_time"] = localtime(message.date).strftime("%H:%M")
            messages.append(message_dict)

        context["messages"] = messages
        context["user"] = self.request.user
        context["admin_ids"] = UserModel.objects.filter(is_superuser=True).values_list("id", flat=True)

        return context

    def form_valid(self, form):
        message = form.save(commit=False)
        message.chat = self.get_chat()
        message.user = self.request.user
        message.save()

        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, generic.FormView):
    template_name = "profile.html"
    # model = get_user_model()
    # form_class = ProfileForm


class CourseView(LoginRequiredMixin, generic.ListView):
    template_name = "course.html"
    model = Lecture
   # form_class = LecturePlatformUserForm


class AdminReviewListView(LoginRequiredMixin, generic.ListView):
    template_name = "admin-review-list.html"
    model = HomeWork


class AdminReviewTaskView(LoginRequiredMixin, generic.DetailView):
    template_name = "admin-review-task.html"
    model = HomeWork
    # form_name = ReviewForm


class AdminDashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = "admin-dashboard.html"


class AdminStudentsView(LoginRequiredMixin, generic.ListView):
    template_name = "admin-students.html"
    model = get_user_model()


class AdminBoxesView(LoginRequiredMixin, generic.ListView):
    template_name = "admin-boxes.html"
    model = StartBox


class BoxApplicationView(LoginRequiredMixin, generic.FormView):
    template_name = "box-application.html"
    model = StartBox
    form_name = BoxApplicationForm


class AdminLectureList(LoginRequiredMixin, generic.ListView):
    template_name = "admin-lecture-list.html"
    model = Lecture


