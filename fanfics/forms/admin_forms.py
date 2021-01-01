from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q

from common.models import Fanfic, FandomFanfic, Fandom, CharacterFanfic, \
    Pairing
from fanfics.widgets.widget import SelectCustomWidget


class FanficForm(forms.ModelForm):
    primary_fandom = forms.ModelChoiceField(
        queryset=Fandom.objects.all(),
        required=True,
        widget=SelectCustomWidget(
            attrs={'class': 'custom-select'}))
    secondary_fandom = forms.ModelChoiceField(
        queryset=Fandom.objects.all(),
        required=False,
        widget=SelectCustomWidget(
            attrs={'class': 'custom-select-with-blank'}))

    class Meta:
        model = Fanfic
        exclude = ('id',)

    def __init__(self, *args, **kwargs):
        super(FanficForm, self).__init__(*args, **kwargs)
        instance = self.instance
        if instance.id:
            # modify, not create
            self.fields['primary_fandom'].initial = \
                self.instance.get_primary_fandom()
            self.fields['secondary_fandom'].initial = \
                self.instance.get_secondary_fandom()

    def clean(self):
        # clean
        super(FanficForm, self).clean()

        try:
            average_score = self.cleaned_data.get('average_score')
            if average_score:
                average_score = float(average_score)

                if average_score < 0 or average_score > 5:
                    msg = (
                        "The average score has to be greater or equal to zero,"
                        " and less than 6.")
                    self.add_error('average_score', msg)

        except Exception:
            self.add_error('average_score', "The value is not valid")
            raise ValidationError("The value is not valid.")

        try:
            primary_fandom = self.cleaned_data.get('primary_fandom')
            secondary_fandom = self.cleaned_data.get(
                'secondary_fandom', None)
        except Exception:
            raise ValidationError("The value of the fandom is wrong.")

        if primary_fandom == secondary_fandom:
            self.add_error('secondary_fandom', 'The fandom cannot be the '
                                               'same as the primary one.')
        return self.cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        fanfic = super(FanficForm, self).save(commit=False)
        fanfic.save()
        primary_fandom = self.cleaned_data.get('primary_fandom',
                                               None)
        secondary_fandom = self.cleaned_data.get('secondary_fandom', None)

        # delete previous relation
        primary_added = False
        secondary_added = False
        fandom_fanfics = FandomFanfic.objects.filter(fanfic=fanfic)
        for fandom_fanfic in fandom_fanfics:
            fandom = fandom_fanfic.fandom
            if fandom == primary_fandom:
                fandom_fanfic.is_primary = True
                fandom_fanfic.save()
                primary_added = True
            elif fandom == secondary_fandom:
                fandom_fanfic.is_primary = False
                fandom_fanfic.save()
                secondary_added = True
            else:
                # Delete
                fandom_fanfic.delete()
                # delete pairings
                Pairing.objects.filter(fanfic=fanfic).filter(
                    Q(character_one__fandom=fandom) | Q(
                        character_two__fandom=fandom)).delete()
                # delete character associations to that fanfic of the fandom
                # deleted
                CharacterFanfic.objects.filter(
                    fanfic=fanfic, character__fandom=fandom).delete()

        if primary_added is False:
            FandomFanfic.objects.create(fandom=primary_fandom, fanfic=fanfic,
                                        is_primary=True)

        if secondary_added is False and secondary_fandom:
            FandomFanfic.objects.create(fandom=secondary_fandom, fanfic=fanfic,
                                        is_primary=False)

        return fanfic
