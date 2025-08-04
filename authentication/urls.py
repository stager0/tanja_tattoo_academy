from django.urls import path
from django.views.generic import TemplateView

from authentication.views import RegisterView, ChangePasswordView, ChangePasswordRequestView

urlpatterns = [
    path("accounts/register/", RegisterView.as_view(), name="register"),
    path("accounts/change_password_request/", ChangePasswordRequestView.as_view(), name="change_password_request"),
    path("accounts/change_password/", ChangePasswordView.as_view(), name="change_password"),
    path("accounts/email_sent_info/", TemplateView.as_view(template_name="registration/change_password_email_send_info.html"), name="email_sent_info"),
    path("accounts/change_password_success/", TemplateView.as_view(template_name="registration/change_password_success.html"), name="change_password_success"),
    path("404/", TemplateView.as_view(template_name="custom-errors/404.html"), name="custom_404"),
    path("500/", TemplateView.as_view(template_name="custom-errors/500.html"), name="custom_500"),
    path("thank_you/", TemplateView.as_view(template_name="user_templates/success-pay.html"), name="thank_you"),
    path("answer_to_form/", TemplateView.as_view(template_name="user_templates/answer_to_index_form.html"),name="answer"),
    path("success_pay/", TemplateView.as_view(template_name="user_templates/success-pay.html"), name="success_pay"),
    path("cancel_pay/", TemplateView.as_view(template_name="user_templates/cancel-pay.html"), name="cancel_pay"),
    path("error_pay/", TemplateView.as_view(template_name="user_templates/error-pay.html"), name="error_pay"),
]
