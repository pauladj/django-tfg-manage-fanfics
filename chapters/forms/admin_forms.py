from django import forms
from django.core.exceptions import ValidationError

from common.models import Chapter
from fanfics.widgets.widget import SelectCustomWidget


class ChapterChangeForm(forms.ModelForm):
    class Meta:
        model = Chapter
        exclude = ('id', 'fanfic')

    def clean(self):
        super(ChapterChangeForm, self).clean()
        clean_number_of_chapter(self)
        return self.cleaned_data

    def validate_unique(self):
        exclude = self._get_validation_exclusions()
        exclude.remove(
            'fanfic')  # allow checking against the missing attribute
        try:
            self.instance.validate_unique(exclude=exclude)
        except ValidationError as e:
            self._update_errors(e.message_dict)


class ChapterAddForm(forms.ModelForm):
    class Meta:
        model = Chapter
        exclude = ('id',)
        widgets = {
            'fanfic': SelectCustomWidget(attrs={'class': 'custom-select'})
        }

    def clean(self):
        super(ChapterAddForm, self).clean()
        clean_number_of_chapter(self)

        return self.cleaned_data


def clean_number_of_chapter(self):
    """ Clean the number of the chapter """
    try:
        chapter = self.cleaned_data.get('num_chapter')
        chapter = int(chapter)

        if chapter <= 0:
            self.add_error(
                'num_chapter', "The number of the chapter has to be greater "
                               "than zero.")
    except Exception:
        self.add_error('num_chapter', "The value is not valid")


