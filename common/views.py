# import the logging library
import logging
import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.views import View
# Get an instance of a logger
from django.views.generic import ListView

from common.models import Fanfic
from notifier.models import Notification
from users.models import Following, CustomUser

logger = logging.getLogger(__name__)


class SearchView(LoginRequiredMixin, ListView):
    """ Search """
    template_name = 'search.html'
    context_object_name = "search_list"
    paginate_by = 15

    def get_queryset(self):
        query = []
        self.where = None
        self.search_text = None

        where = "fanfic"  # default
        if "where" in self.request.GET:
            where = self.request.GET.get("where")
            if where != "user" and where != "fanfic":
                return query
        self.where = where

        if "text" not in self.request.GET:
            return query

        term_to_search = self.request.GET.get("text")
        term_to_search = term_to_search.rstrip().lstrip()

        if len(term_to_search) == 0:
            return query

        self.search_text = term_to_search

        if where == "fanfic":
            query = Fanfic.objects.filter(
                Q(name__icontains=term_to_search) | Q(
                    author__icontains=term_to_search)).order_by('id')
        elif where == "user":
            query = CustomUser.objects.filter(Q(
                name_surname__icontains=term_to_search) | Q(
                username__icontains=term_to_search)).order_by('id')

        return query

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context['where'] = self.where

        query_string_params = self.request.META['QUERY_STRING']
        if "page" in query_string_params:
            query_string_params_two = re.compile("^page=\d+&?").split(
                query_string_params)
            if len(query_string_params_two) == 2:
                query_string_params_two = query_string_params_two[1]
            else:
                query_string_params_two = ''
        else:
            query_string_params_two = query_string_params
        context['pagination_append'] = "&" + query_string_params_two

        context['search_text'] = self.search_text
        return context


class DashboardView(LoginRequiredMixin, ListView):
    """ See the dashboard """
    template_name = 'dashboard.html'
    context_object_name = "user_notifications"
    paginate_by = 20

    def get_queryset(self):
        users_following = Following.objects.filter(
            user_one=self.request.user).values_list(
            'user_two__id', flat=True)

        a = Notification.objects.filter(in_feed=True).filter(
            subject_user__in=users_following, reverse=False)
        b = Notification.objects.filter(in_feed=True).filter(
            target__in=users_following, reverse=True)
        query = a | b
        query = query.order_by('-when')
        return query

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['menu'] = 'home'
        return context


class EntryPointView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated is True:
            return redirect('common:home')
        else:
            return redirect('pages:home')


class BaseView(View):
    """ Allow methods like DELETE and PUT """

    def dispatch(self, request, *args, **kwargs):
        method = self.request.POST.get('_method', '').lower()
        handler = None
        if method == 'put':
            handler = getattr(self, "put", self.http_method_not_allowed)
        if method == 'delete':
            handler = getattr(self, "delete", self.http_method_not_allowed)
        if handler is not None:
            return handler(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)
