"""
URL configuration for tattoo_academy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from web.telegram_bot import webhook_telegram
from web.views import RegisterView, ChangePasswordRequestView, ChangePasswordView, IndexView, CreateCheckoutSessionView, \
    Webhook

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("thank_you/", TemplateView.as_view(template_name="user_templates/success-pay.html"), name="thank_you"),
    path("answer_to_form/", TemplateView.as_view(template_name="user_templates/answer_to_index_form.html"), name="answer"),
    path("success_pay/", TemplateView.as_view(template_name="user_templates/success-pay.html"), name="success_pay"),
    path("cancel_pay/", TemplateView.as_view(template_name="user_templates/cancel-pay.html"), name="cancel_pay"),
    path("error_pay/", TemplateView.as_view(template_name="user_templates/error-pay.html"), name="error_pay"),
    path("checkout_session/", CreateCheckoutSessionView.as_view(), name="checkout_session"),
    path("stripe_webhook/", Webhook.as_view(), name="webhook"),
    path("telegram_webhook/<str:token>/", webhook_telegram, name="webhook_telegram"),
    path('admin/', admin.site.urls),
    path("platform/", include("web.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", RegisterView.as_view(), name="register"),
    path("accounts/change_password_request/", ChangePasswordRequestView.as_view(), name="change_password_request"),
    path("accounts/change_password/", ChangePasswordView.as_view(), name="change_password"),
    path("accounts/email_sent_info/", TemplateView.as_view(template_name="registration/change_password_email_send_info.html"), name="email_sent_info"),
    path("accounts/change_password_success/", TemplateView.as_view(template_name="registration/change_password_success.html"), name="change_password_success"),
    path("404/", TemplateView.as_view(template_name="custom-errors/404.html"), name="custom_404"),
    path("500/", TemplateView.as_view(template_name="custom-errors/500.html"), name="custom_500")
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = "web.views.custom_404_view"
handler500 = "web.views.custom_500_view"