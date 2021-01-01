from django.contrib import admin, messages
from django.db import transaction

from characters.forms.admin_forms import CharacterChangeForm, CharacterAddForm
from common.models import Character, Type, CharacterFanfic, Pairing


class TypeListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'media type'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'media'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        types = Type.objects.values('name')

        list_tuples = tuple([(x['name'], x['name']) for x in types])
        return list_tuples

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        type_name = self.value()
        if type_name:
            # the user filtered by type
            type_obj = Type.objects.filter(name=type_name)
            if type_obj.exists():
                type_obj = type_obj.first()
                queryset = queryset.filter(fandom__type=type_obj)

            return queryset


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_surname',
                    'fandom', 'type')
    list_display_links = ('name_surname',)
    list_filter = (TypeListFilter, 'fandom')

    search_fields = ('name_surname', 'fandom__name')

    actions = ['merge_characters']

    def type(self, obj):
        return obj.fandom.type

    def get_form(self, request, obj=None, **kwargs):
        """ Get the form to show """
        if obj:
            self.form = CharacterChangeForm
        else:
            self.form = CharacterAddForm

        return super(CharacterAdmin, self).get_form(request, obj, **kwargs)

    def merge_characters(self, request, queryset):
        """ Merge the characters if they are the same, and they are in the
        same fandom"""
        try:
            with transaction.atomic():
                if queryset.count() > 2:
                    self.message_user(request,
                                      "You can only join two characters at "
                                      "the same time.",
                                      level=messages.ERROR)
                else:
                    character_to_keep = queryset.first()
                    fandom_one = character_to_keep.fandom

                    character_to_go = queryset.last()
                    fandom_two = character_to_go.fandom

                    if fandom_one.id != fandom_two.id:
                        self.message_user(request,
                                          "The characters have to be "
                                          "in the same "
                                          "fandom.",
                                          level=messages.ERROR)
                    else:
                        # only two selected, same fandom, join them

                        # Character fanfic
                        fanfic_characters_to_keep = list(
                            CharacterFanfic.objects.filter(
                                character=character_to_keep).values_list(
                                'fanfic__id',
                                flat=True))
                        CharacterFanfic.objects.exclude(
                            fanfic__id__in=fanfic_characters_to_keep).filter(
                            character=character_to_go).update(
                            character=character_to_keep)

                        # Pairing
                        Pairing.objects.filter(
                            character_one=character_to_keep,
                            character_two=character_to_go).delete()
                        Pairing.objects.filter(
                            character_two=character_to_keep,
                            character_one=character_to_go).delete()

                        Pairing.objects.filter(
                            character_one=character_to_go).update(
                            character_one=character_to_keep)
                        Pairing.objects.filter(
                            character_two=character_to_go).update(
                            character_two=character_to_keep)

                        character_to_go.delete()

                        # success
                        self.message_user(request,
                                          "The characters have been merged.",
                                          level=messages.SUCCESS)

        except Exception:
            self.message_user(request,
                              "There was an unexpected error.",
                              level=messages.ERROR)

    merge_characters.short_description = "Merge the characters, they are" \
                                         " the same"
