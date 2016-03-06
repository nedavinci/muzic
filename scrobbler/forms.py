import datetime

from django import forms
from django.core.exceptions import ValidationError


class TimestampField(forms.DateTimeField):
    def to_python(self, value):
        try:
            value = datetime.datetime.fromtimestamp(int(value))
            return super(TimestampField, self).to_python(value)
        except ValueError:
            raise ValidationError(self.error_messages['invalid'], code='invalid')


class SubmissionForm(forms.Form):
    artist = forms.CharField()
    track = forms.CharField()
    album = forms.CharField()
    timestamp = TimestampField()
    tracknumber = forms.IntegerField(max_value=255, min_value=1)
    source = forms.CharField()
    rating = forms.CharField()
    length = forms.IntegerField()
    mbid = forms.CharField(max_length=36, strip=True)
    # 'a': 'artist',
    # 't': 'track',
    # 'i': 'timestamp',
    # 'o': 'source',
    # 'r': 'rating',
    # 'l': 'length',
    # 'b': 'album',
    # 'n': 'tracknumber',
    # 'm': 'mbid'

    def __init__(self, *args, **kwargs):
        super(SubmissionForm, self).__init__(*args, **kwargs)
        self.fields['timestamp'].min_value = datetime.datetime.now() - datetime.timedelta(days=365)
