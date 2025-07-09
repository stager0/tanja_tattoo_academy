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
from web.models import ResetCode


class RegisterView(CreateView):
    form_class = CustomRegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        code_obj = form.cleaned_data.get("code")
        if code_obj:
            code_obj.is_activated = True
            code_obj.activated_date = timezone.now()
            code_obj.save()

        email = form.cleaned_data.get("email", "")
        full_name = form.cleaned_data.get("first_name", "") + " " + form.cleaned_data.get("last_name", "")
        if email and full_name:
            send_after_register_email(email=email, full_name=full_name)
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
