import json
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import ListView

from common.models import Fanfic as fanfic_model, Review, Chapter, Character, \
    Related
from common.tasks import scrape_and_add_fanfic
from common.views import BaseView
# Get an instance of a logger
from fanfics.custom_models import FanficWeb as Fanfic
from fanfics.forms.web_forms import UserSubmittedErrorForm

logger = logging.getLogger(__name__)


class AddExternalFanfic(LoginRequiredMixin, View):
    """ Add an external fanfic """
    template_name = 'add_external_fanfic.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request):
        url_fanfic = request.POST.get("url_fanfic")
        fanfic = Fanfic(url_fanfic)
        url_errors = fanfic.url_without_errors()

        if "Error" in url_errors:
            msg_error = url_errors
            messages.error(request, msg_error)
            logger.error("Error in fanfic url {}".format(msg_error))
            return render(request, self.template_name,
                          {"url_fanfic": url_fanfic,
                           "error": "error"})
        else:
            url_fanfic = url_errors

        try:
            cleaned_url = fanfic.get_cleaned_url()
            url_in_system = fanfic_model.objects.filter(
                web__icontains=cleaned_url).exists()
            if url_in_system is True:
                messages.error(request, "This fanfic is already in the "
                                        "system")
                return render(request, self.template_name,
                              {"url_fanfic": url_fanfic,
                               "error": "error"})

            online = fanfic.check_if_online()

            if online is False:
                # url not working anymore
                messages.error(request, "Sorry, the url doesn't seem to"
                                        " be working "
                                        "right now.")
                return render(request, self.template_name,
                              {"url_fanfic": url_fanfic,
                               "error": "error"})
            current_user = request.user.id
            scrape_and_add_fanfic.delay(url_fanfic, current_user)
            logger.info("Fanfic added to celery queue")
            return redirect(reverse('fanfics:external_done'))
        except Exception as e:
            # couldn't parse well, server error, it's our fault
            logger.error("Error adding external fanfic: {}".format(e))
            messages.error(request, "We have a server error and we'll "
                                    " fix it soon. It's our fault and we "
                                    "apologize.")
            return redirect(reverse('fanfics:external_add'))


class AddExternalFanficDone(LoginRequiredMixin, View):
    ''' Show that an external fanfic has been added and user has to wait '''
    template_name = 'add_external_fanfic_done.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class FanficErrorsView(LoginRequiredMixin, BaseView):
    """ Submit an error of a fanfic """

    def post(self, request, fanfic_id=None):
        if fanfic_id is None:
            raise PermissionDenied()

        fanfic = get_object_or_404(fanfic_model, id=fanfic_id)

        form = UserSubmittedErrorForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.fanfic = fanfic
            report.save()
            messages.success(request,
                             "Your report has been submitted. "
                             "Thank you for your time.")
        else:
            logger.error("Error trying to save user report {}".format(
                form.errors))
            messages.error(request, "There was an error trying to save your "
                                    "report.")
        return redirect('fanfics:fanfic', fanfic_id=fanfic_id)


class FanficView(LoginRequiredMixin, ListView):
    """ Show a fanfic """
    template_name = 'fanfic.html'
    context_object_name = "reviews"
    paginate_by = 10

    def get_queryset(self):
        fanfic_id = self.kwargs['fanfic_id']
        queryset = Review.objects.filter(
            fanfic=fanfic_id).exclude(
            user=self.request.user).order_by('-date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(FanficView, self).get_context_data(**kwargs)
        context['fanfic'] = fanfic_model.objects.get(
            id=self.kwargs['fanfic_id'])

        current_user_review = Review.objects.filter(user=self.request.user,
                                                    fanfic=self.kwargs[
                                                        'fanfic_id'])
        if current_user_review.count() > 0:
            context['review_user'] = current_user_review.first()

        chapters = Chapter.objects.filter(
            fanfic=self.kwargs['fanfic_id'])
        context['chapters'] = chapters
        context['error_form'] = UserSubmittedErrorForm()
        context['related'] = Related.objects.filter(fanfic_one=context[
            'fanfic'])

        return context


class FanficCharactersView(LoginRequiredMixin, BaseView):
    """ Get possible characters for a fanfic """

    def get(self, request, fanfic_id):
        if fanfic_id is None or request.is_ajax() is False:
            return HttpResponse("Method not Allowed", status=400)

        fanfic = get_object_or_404(fanfic_model, id=fanfic_id)

        fandom_one = fanfic.get_primary_fandom()
        fandom_two = fanfic.get_secondary_fandom()

        characters = Character.objects.filter(Q(
            fandom=fandom_one) | Q(fandom=fandom_two)).distinct()

        character_list = []
        character_obj = {"values": character_list}
        for c in characters:
            obj = {
                "text": c.name_surname,
                "value": c.id
            }
            character_list.append(obj)

        return HttpResponse(json.dumps(character_obj), status=200)
