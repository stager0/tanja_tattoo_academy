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

from web.telegram_bot import webhook_telegram
from web.views import IndexView, CreateCheckoutSessionView, Webhook

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("checkout_session/", CreateCheckoutSessionView.as_view(), name="checkout_session"),
    path("stripe_webhook/", Webhook.as_view(), name="webhook"),
    path("telegram_webhook/<str:token>/", webhook_telegram, name="webhook_telegram"),
    path('admin/', admin.site.urls),
    path("platform/", include("web.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("authentication.urls"))
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = "web.views.custom_404_view"
handler500 = "web.views.custom_500_view"