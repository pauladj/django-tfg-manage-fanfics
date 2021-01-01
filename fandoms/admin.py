from django.contrib import admin

from common.models import Fandom


@admin.register(Fandom)
class FandomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'avatar')
    list_display_links = ('name',)
    list_filter = ('type__name',)

    search_fields = ('name',)

    def get_queryset(self, request):
        qs = super(FandomAdmin, self).get_queryset(request)
        return qs.exclude(name="Other")
