from django import forms
from django.db import transaction

from common.models import Character, CharacterFanfic, FandomFanfic
from fanfics.widgets.widget import SelectCustomWidget


class CharacterAddForm(forms.ModelForm):
    class Meta:
        model = Character
        exclude = ('id',)

        widgets = {
            'fandom': SelectCustomWidget(attrs={'class': 'custom-select'})
        }


class CharacterChangeForm(forms.ModelForm):
    class Meta:
        model = Character
        exclude = ('id',)
        widgets = {
            'fandom': SelectCustomWidget(attrs={'class': 'custom-select'})
        }

    @transaction.atomic
    def save(self, commit=True):
        character = super(CharacterChangeForm, self).save(commit=False)

        old_fandom = Character.objects.get(id=character.id).fandom

        new_fandom = character.fandom

        if old_fandom.id != new_fandom.id:
            # the old fandom is not the same as the new one
            fandom_fanfic_with_old_fandom = FandomFanfic.objects.filter(
                fandom=old_fandom)
            for fandom_fanfic in fandom_fanfic_with_old_fandom:
                fanfic_with_old_fandom = fandom_fanfic.fanfic

                primary = fanfic_with_old_fandom.get_primary_fandom()
                secondary = fanfic_with_old_fandom.get_secondary_fandom()

                if primary.id == new_fandom.id:
                    pass
                elif secondary and secondary.id == new_fandom.id:
                    pass
                else:
                    CharacterFanfic.objects.filter(
                        character__id=character.id,
                        fanfic=fanfic_with_old_fandom).delete()

                    # there's a signal to delete the pairings

        if commit:
            character.save()
        return character
