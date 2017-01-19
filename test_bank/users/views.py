# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import User
from django.contrib.auth.decorators import login_required


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False
    def get_redirect_url(self):
        return reverse('borrowing:home')


class UserUpdateView(LoginRequiredMixin, UpdateView):

    fields = ['first_name', 'last_name']
    model = User
    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail')

    def get_object(self):
        return User.objects.get(username=self.request.user.username)
