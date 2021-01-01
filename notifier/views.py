from notifier import models

from django.views.generic import ListView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


class NotificationsView(LoginRequiredMixin, ListView):
    template_name = 'see_all_notifications.html'
    context_object_name = "user_notifications"
    paginate_by = 30

    def get_queryset(self):
        return models.Notification.objects.filter(
            target=self.request.user, in_top_bar=True).order_by('-when')
