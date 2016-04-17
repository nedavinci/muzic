from django.utils.translation import ugettext as _
from django import forms


class FieldSelectForm(forms.Form):
    def __init__(self, list_display_choices, *args, **kwargs):
        super(FieldSelectForm, self).__init__(*args, **kwargs)
        self.fields['list_display_select'].choices = list_display_choices

    list_display_select = forms.MultipleChoiceField(
            label=_('Choose list columns'), choices=(), widget=forms.CheckboxSelectMultiple
    )
