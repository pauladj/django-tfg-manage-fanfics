from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from common.models import Fandom, Type


class FandomsView(LoginRequiredMixin, ListView):
    ''' Show fandoms of media type '''
    template_name = 'fandoms.html'
    context_object_name = "fandoms"
    paginate_by = 30

    def get_queryset(self):
        self.media_type = Type.objects.get(name=self.kwargs['media_type'])
        fandoms = Fandom.objects.filter(type=self.media_type)

        self.alphabet_letter = self.request.GET.get('starts_with', None)
        if self.alphabet_letter:
            fandoms = fandoms.filter(
                name__istartswith=self.alphabet_letter).order_by('name')
        else:
            fandoms = fandoms.order_by('id')

        return fandoms

    def get_context_data(self, **kwargs):
        context = super(FandomsView, self).get_context_data(**kwargs)

        context['menu'] = 'browse'
        context['media_type'] = self.media_type.name
        if self.alphabet_letter:
            context['letter'] = self.alphabet_letter

        return context
