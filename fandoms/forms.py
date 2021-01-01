from django import forms

from common.choices import SORT_CHOICES, GENRES_CHOICES, LENGTH_CHOICES, \
    STATUS_CHOICES, RATING_CHOICES


class FilterFanficsByFandom(forms.Form):
    sort_by = forms.ChoiceField(choices=SORT_CHOICES, initial=0,
                                required=False)
    genre = forms.ChoiceField(choices=GENRES_CHOICES, initial=0,
                              required=False)
    language = forms.CharField(required=False)
    length = forms.ChoiceField(choices=LENGTH_CHOICES, initial=0,
                               required=False)
    status = forms.ChoiceField(choices=STATUS_CHOICES, initial=0,
                               required=False)
    rating = forms.ChoiceField(choices=RATING_CHOICES, initial=0,
                               required=False)

    character_a = forms.IntegerField(required=False)
    character_b = forms.IntegerField(required=False)

