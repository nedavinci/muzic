from django.contrib import admin
from django.db import models as django_models
from django.utils.functional import curry
from django.utils.html import format_html
from django_select2.forms import Select2Widget

from .. import models
from .fields import CoverFileInput, RelativeSortedFilePathField
from .widgets import ContenteditableInput


class TrackInline(admin.TabularInline):
    formfield_overrides = {
        django_models.FilePathField: {
            'form_class': RelativeSortedFilePathField},
        django_models.CharField: {
            'widget': ContenteditableInput},
    }
    model = models.Track
    can_delete = False
    extra = 0
    readonly_fields = ('length', 'rg_peak', 'rg_gain')
    exclude = ['lirycs', ]
    initial = []

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(TrackInline, self).get_formset(request, obj, **kwargs)
        if request.method == 'GET':
            formset.__init__ = curry(formset.__init__, initial=self.initial)
        return formset

    # def has_add_permission(self, request):
    #     return False


class ReleaseInline(admin.TabularInline):
    model = models.Release
    formfield_overrides = {
        django_models.ForeignKey: {
            'widget': Select2Widget(attrs={
                'data-width': '300px',
            })
        }
    }
    extra = 1


class CoverInline(admin.TabularInline):
    # form = CoverForm
    template = 'admin/covers_tabular.html'
    fields = ('thumb', 'cover', 'covertype', 'sort')
    readonly_fields = ('thumb',)
    model = models.Cover
    ordering = ('covertype', 'sort')
    extra = 0
    formfield_overrides = {
        django_models.ImageField: {
            'widget': CoverFileInput(attrs={
                'accept': "image/*"
            }, multiple_input_name='cover_set-files-multi')
        }
    }

    def thumb(self, obj):
        return format_html(
            """
            <a href="{0}">
                <img src="{0}" style="max-width: 150px; max-height: 150px">
            </a>
            """, obj.cover.url, None)
    thumb.allow_tags = True
