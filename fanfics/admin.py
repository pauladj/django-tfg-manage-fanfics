# Register your models here.

from django.contrib import admin, messages
from django.db import transaction
from django.db.models import Q

from common.models import Fanfic, Fandom, FandomFanfic, Type, CharacterFanfic, \
    Pairing, SubmittedReport
from fanfics.forms.admin_forms import FanficForm
from fanfics.widgets.widget import SelectCustomWidget


class FandomListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'fandom'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'fandom'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        fandoms = Fandom.objects.values('id', 'name')

        list_tuples = tuple([(x['id'], x['name']) for x in fandoms])
        return list_tuples

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        fandom_id = self.value()
        if fandom_id:
            # the user filtered by fandom
            fanfics_ids_with_fandom = list(FandomFanfic.objects.filter(
                fandom__id=fandom_id).distinct().values_list('fanfic__id',
                                                             flat=True))

            queryset = queryset.filter(id__in=fanfics_ids_with_fandom)
            return queryset


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

                fanfics_ids_with_fandom = list(FandomFanfic.objects.filter(
                    fandom__type=type_obj).distinct().values_list(
                    'fanfic__id', flat=True))

                queryset = queryset.filter(id__in=fanfics_ids_with_fandom)
            return queryset


@admin.register(Fanfic)
class FanficAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',
                    'language', 'complete', 'date_added', 'last_time_checked',
                    'average_score', 'primary_fandom', 'secondary_fandom')
    list_display_links = ('name',)
    list_filter = (
        'author', 'language', 'complete', 'rating', TypeListFilter,
        FandomListFilter)

    search_fields = ('name', 'author')

    form = FanficForm

    def primary_fandom(self, obj):
        if obj:
            return obj.get_primary_fandom()

    def secondary_fandom(self, obj):
        if obj:
            return obj.get_secondary_fandom()


class FandomListFilterCharacterFanfic(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'fandom'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'fandom'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        fandoms = Fandom.objects.values('id', 'name')

        list_tuples = tuple([(x['id'], x['name']) for x in fandoms])
        return list_tuples

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        fandom_id = self.value()
        if fandom_id:
            # the user filtered by fandom
            fanfics_ids_with_fandom = list(FandomFanfic.objects.filter(
                fandom__id=fandom_id).distinct().values_list('fanfic__id',
                                                             flat=True))

            queryset = queryset.filter(fanfic__id__in=fanfics_ids_with_fandom)
            return queryset


class TypeListFilterCharacterFanfic(admin.SimpleListFilter):
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

                fanfics_ids_with_fandom = list(FandomFanfic.objects.filter(
                    fandom__type=type_obj).distinct().values_list(
                    'fanfic__id', flat=True))

                queryset = queryset.filter(
                    fanfic__id__in=fanfics_ids_with_fandom)
            return queryset


@admin.register(CharacterFanfic)
class CharacterFanficAdmin(admin.ModelAdmin):
    list_display = ('id', 'fanfic', 'character', 'pairing_id')
    list_display_links = ('fanfic',)

    list_filter = (
        TypeListFilterCharacterFanfic,
        FandomListFilterCharacterFanfic)

    search_fields = ('character__name_surname', 'fanfic__name')

    fields = ('fanfic', 'character')

    actions = ['create_pairing', 'delete_pairing']

    def has_change_permission(self, request, obj=None):
        return False

    def pairing_id(self, obj):
        a = list(Pairing.objects.filter(fanfic=obj.fanfic).filter(Q(
            character_one=obj.character) | Q(
            character_two=obj.character)).values_list(
            'id', flat=True))
        return a

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "character":
            # change widget
            kwargs['widget'] = SelectCustomWidget(
                attrs={'class': 'custom-select character-select'})
        elif db_field.name == "fanfic":
            # change widget
            kwargs['widget'] = SelectCustomWidget(
                attrs={'class': 'custom-select fanfic-select'})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def create_pairing(self, request, queryset):
        """ Create pairing between two characters for a fanfic """
        try:
            with transaction.atomic():
                if queryset.count() > 2:
                    self.message_user(request,
                                      "A pairing can only have two "
                                      "characters at the same time.",
                                      level=messages.ERROR)
                else:
                    first = queryset.first()
                    second = queryset.last()
                    if first.fanfic.id != second.fanfic.id:
                        # error, different fanfics
                        self.message_user(request,
                                          "The selected characters are from "
                                          "different fanfics.",
                                          level=messages.ERROR)
                    else:
                        p = Pairing.objects.filter(
                            fanfic=first.fanfic).filter(Q(
                            character_one=first.character,
                            character_two=second.character) | Q(
                            character_one=second.character,
                            character_two=first.character))
                        if p.exists():
                            # error, the pairing already exists
                            self.message_user(request,
                                              "This pairing already exists.",
                                              level=messages.ERROR)
                        else:
                            Pairing.objects.create(
                                fanfic=first.fanfic,
                                character_one=first.character,
                                character_two=second.character)
                            # success
                            self.message_user(
                                request,
                                "The pairing has been created.",
                                level=messages.SUCCESS)
        except Exception:
            self.message_user(request,
                              "There was an unexpected error.",
                              level=messages.ERROR)

    create_pairing.short_description = "Create a pairing between the " \
                                       "characters"

    def delete_pairing(self, request, queryset):
        """ Delete the pairing between two characters for a fanfic """
        try:
            with transaction.atomic():
                if queryset.count() > 2:
                    self.message_user(request,
                                      "A pairing can only have two "
                                      "characters at the same time.",
                                      level=messages.ERROR)
                else:
                    first = queryset.first()
                    second = queryset.last()
                    if first.fanfic.id != second.fanfic.id:
                        # error, different fanfics
                        self.message_user(request,
                                          "The selected characters are from "
                                          "different fanfics.",
                                          level=messages.ERROR)
                    else:
                        p = Pairing.objects.filter(
                            fanfic=first.fanfic).filter(Q(
                            character_one=first.character,
                            character_two=second.character) | Q(
                            character_one=second.character,
                            character_two=first.character))
                        if p.exists():
                            # the pairing already exists
                            p.delete()
                            # success
                            self.message_user(
                                request,
                                "The pairing has been deleted.",
                                level=messages.SUCCESS)
                        else:
                            # the pairing does not exist
                            self.message_user(request,
                                              "This pairing does not "
                                              "exists.",
                                              level=messages.ERROR)
        except Exception:
            self.message_user(request,
                              "There was an unexpected error.",
                              level=messages.ERROR)

    delete_pairing.short_description = "Delete the pairing"


@admin.register(SubmittedReport)
class SubmittedReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'fanfic', 'date', 'issue', 'comment')
    list_display_links = ('fanfic',)

    search_fields = ('fanfic__name',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
