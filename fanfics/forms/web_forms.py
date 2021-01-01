from django import forms

from common.models import SubmittedReport


class UserSubmittedErrorForm(forms.ModelForm):
    class Meta:
        model = SubmittedReport
        exclude = ('id', 'date', 'user', 'fanfic')
