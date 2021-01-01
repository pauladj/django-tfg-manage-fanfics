import re

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView

from common.models import Fandom, FandomFanfic, CharacterFanfic
from fandoms.forms import FilterFanficsByFandom


class FanficsOfFandomView(LoginRequiredMixin, ListView):
    """ Show fanfics of fandom """
    template_name = 'fanfics_of_fandom.html'
    context_object_name = "fanfics"
    paginate_by = 15

    def get_queryset(self):
        self.fandom = Fandom.objects.get(id=self.kwargs['fandom_id'])
        fanfics = FandomFanfic.objects.filter(fandom=self.fandom)

        try:
            # get the queryset filtered
            if "sort_by" in self.request.GET:
                form = FilterFanficsByFandom(self.request.GET)
                if form.is_valid():
                    sort_by = form.cleaned_data.get('sort_by', 0)
                    language = form.cleaned_data.get('language', 0)
                    genre = form.cleaned_data.get('genre', 0)
                    length = form.cleaned_data.get('length', 0)
                    status = form.cleaned_data.get('status', 0)
                    rating = form.cleaned_data.get('rating', 0)
                    character_a = form.cleaned_data.get('character_a', 0)
                    character_b = form.cleaned_data.get('character_b', 0)

                    # LANGUAGE
                    if language != 0 and language != "0":
                        fanfics = fanfics.filter(
                            fanfic__language__iexact=language)

                    # GENRE
                    if genre != 0 and genre != "0":
                        fanfics = fanfics.filter(Q(
                            fanfic__genre1__iexact=genre) | Q(
                            fanfic__genre2__iexact=genre) | Q(
                            fanfic__genre3__iexact=genre) | Q(
                            fanfic__genre4__iexact=genre))

                    # LENGTH
                    words = 1000
                    if length == "0" or length == 0:
                        pass
                    elif length == "1" or length == 1:
                        # < 1K words
                        words = 1000
                        fanfics = fanfics.filter(fanfic__num_words__lt=words)
                    else:
                        if length == "2" or length == 2:
                            # > 10K words
                            words = 10000
                        elif length == "3" or length == 3:
                            # > 40K words
                            words = 40000
                        elif length == "4" or length == 4:
                            # > 60K words
                            words = 60000
                        elif length == "5" or length == 5:
                            # > 100K words
                            words = 100000
                        fanfics = fanfics.filter(fanfic__num_words__gte=words)

                    # STATUS
                    if status == 1 or status == "1":
                        # complete
                        fanfics = fanfics.filter(fanfic__complete=True)
                    elif status == 2 or status == "2":
                        # in progress
                        fanfics = fanfics.exclude(fanfic__complete=True)

                    # RATING
                    if rating == 1 or rating == '1':
                        # K
                        fanfics = fanfics.filter(fanfic__rating='K')
                    elif rating == 2 or rating == '2':
                        # K+
                        fanfics = fanfics.filter(fanfic__rating='K+')
                    elif rating == 3 or rating == '3':
                        # T
                        fanfics = fanfics.filter(fanfic__rating='T')
                    elif rating == 4 or rating == '4':
                        # M
                        fanfics = fanfics.filter(fanfic__rating='M')

                    # CHARACTER A & B
                    fanfics_ids = None
                    if character_a != 0 and character_a != "0" \
                            and character_b != "0" and character_b != 0:
                        fanfics_ids = CharacterFanfic.objects.filter(Q(
                            character__id=character_a) | Q(
                            character__id=character_b)).values_list(
                            'fanfic__id', flat=True)
                    elif character_a != 0:
                        fanfics_ids = CharacterFanfic.objects.filter(
                            character__id=character_a).values_list(
                            'fanfic__id', flat=True)
                    elif character_b != 0:
                        fanfics_ids = CharacterFanfic.objects.filter(
                            character__id=character_b).values_list(
                            'fanfic__id', flat=True)
                    if fanfics_ids is not None:
                        fanfics = fanfics.filter(fanfic__id__in=fanfics_ids)

                    # SORT BY
                    if sort_by == '1' or sort_by == 1:
                        # sort by last updated
                        fanfics = fanfics.order_by(
                            '-fanfic__last_time_updated')
                    elif sort_by == 2 or sort_by == '2':
                        # sort by number of reviews
                        fanfics = sorted(fanfics,
                                         key=lambda t:
                                         t.fanfic.get_num_reviews(),
                                         reverse=True)
                    elif sort_by == 3 or sort_by == '3':
                        # sort by number of followers
                        fanfics = sorted(fanfics,
                                         key=lambda t:
                                         t.fanfic.get_num_of_users(),
                                         reverse=True)
                    else:
                        fanfics = fanfics.order_by('id')

                    return fanfics
                else:
                    raise Exception("There was an unexpected error.")

        except Exception:
            messages.error(self.request, "There was an unexpected error "
                                         "trying to filter the fanfics.")

        fanfics = fanfics.order_by('id')
        return fanfics

    def get_context_data(self, **kwargs):
        context = super(FanficsOfFandomView, self).get_context_data(**kwargs)
        context['form_filter'] = FilterFanficsByFandom(data=self.request.GET)

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
        context['menu'] = 'browse'
        context['fandom'] = self.fandom
        context['media_type'] = self.fandom.type

        return context
