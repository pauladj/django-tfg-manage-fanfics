from django.contrib import admin

from chapters.forms.admin_forms import ChapterChangeForm, ChapterAddForm
from common.models import Chapter


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('fanfic', 'num_chapter', 'title', 'url_chapter')
    list_display_links = ('title',)
    list_filter = ('fanfic',)

    search_fields = ('title', 'url_chapter')

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = ChapterChangeForm
        else:
            self.form = ChapterAddForm
        return super(ChapterAdmin, self).get_form(request, obj, **kwargs)
