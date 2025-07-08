from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from web.forms import CustomRegisterForm


class RegisterView(CreateView):
    form_class = CustomRegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        code_obj = form.cleaned_data["code"]
        code_obj.is_activated = True
        code_obj.activated_date = timezone.now()
        code_obj.save()

        return redirect("login")
