from django.contrib.admin.utils import label_for_field
from django.core.urlresolvers import reverse

from .forms import FieldSelectForm


class FieldSelectMixin(object):
    field_select_form = FieldSelectForm

    def get_list_display(self, request):
        form = self.field_select_form(zip(self.list_display_variants, self.list_display_variants), request.POST)
        session_name = 'list_display_select' + self.__class__.__name__
        if form.is_valid():
            list_display = form.cleaned_data['list_display_select']
            request.session[session_name] = list_display
            return list_display
        elif request.session.get(session_name, False):
            return request.session[session_name]
        return self.list_display_defaults

    def changelist_view(self, request, *args, **kwargs):
        choices = []
        for field_name in self.list_display_variants:
            text = label_for_field(
                field_name, self.model,
                model_admin=self
            )
            choices.append((field_name, text))
        opts = self.model._meta
        changelist_url = 'admin:%s_%s_changelist' % (opts.app_label, opts.model_name)
        kwargs['extra_context'] = dict(
                list_display_form_action_url=reverse(changelist_url),
                list_display_form=self.field_select_form(
                    choices, initial=dict(list_display_select=self.get_list_display(request))
                )
        )
        return super(FieldSelectMixin, self).changelist_view(request, *args, **kwargs)
