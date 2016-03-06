import os
import re
import md5

from django import forms
from django.core.cache import cache
from django_select2.forms import Select2Widget


class RelativeSortedFilePathField(forms.FilePathField):
    def __init__(self, *args, **kwargs):
        super(RelativeSortedFilePathField, self).__init__(*args, **kwargs)
        choices = self.choices
        for i, x in enumerate(choices):
            if x[0]:
                self.choices[i] = (x[1], x[1])
        self.choices = sorted(choices, key=lambda x: x[1])


class AlbumPathField(RelativeSortedFilePathField):
    widget = Select2Widget
    re_disk_subdir = re.compile(r"(^|\/)cd[\d]+/?$", re.IGNORECASE)
    exclude_dirs = []

    def filterchoices(self, choice):
        k, v = choice
        if not k:
            return True
        if re.search(self.re_disk_subdir, k):
            return False

        result = bool(
            filter((lambda x: x.endswith('.flac') or re.match(self.re_disk_subdir, x)), os.listdir(self.path + k))
        ) and k not in self.exclude_dirs
        return result

    def __init__(self, exclude_dirs=[], *args, **kwargs):
        self.exclude_dirs = exclude_dirs
        choices_cache_key = self.__class__.__name__ + '.choices.' + md5.new(
                ','.join(self.exclude_dirs).encode('utf-8')).hexdigest()
        choices = cache.get(choices_cache_key)
        if not choices:
            super(AlbumPathField, self).__init__(*args, **kwargs)
            choices = self.choices
            choices = filter(self.filterchoices, choices)
            choices = sorted(choices, key=lambda x: x[1])
            cache.set(choices_cache_key, choices)
        else:
            acceptable_args = (
                'required', 'widget', 'label', 'initial', 'help_text',
                'error_messages', 'show_hidden_initial', 'validators',
                'localize', 'label_suffix',
            )
            new_kwargs = {
                k: v for k, v in kwargs.iteritems() if k in acceptable_args}
            super(forms.FilePathField, self).__init__(
                choices=(), *args, **new_kwargs)
        self.choices = choices
        self.widget.choices = self.choices


class CoverFileInput(forms.ClearableFileInput):
    def __init__(self, multiple_input_name, attrs=None):
        super(CoverFileInput, self).__init__(attrs=attrs)
        self.multiple_input_name = multiple_input_name

    def value_from_datadict(self, data, files, name):
        fileindex = data.get(name)
        if fileindex:
            fileindex = int(fileindex)
            return files.getlist(self.multiple_input_name)[fileindex]
        upload = super(CoverFileInput, self).value_from_datadict(
                data, files, name)
        return upload
