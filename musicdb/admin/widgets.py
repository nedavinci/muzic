from django.forms import widgets
from django.utils.html import escape


class ContenteditableInput(widgets.TextInput):
    """
    A contenteditable widget to include in your form
    """
    LOWERCASE_WORDS = (
            'a',
            'an',
            'the',
            'and',
            'but',
            'or',
            'nor',
            'for',
            'yet',
            'so',
            'as',
            'at',
            'by',
            'for',
            'in',
            'of',
            'on',
            'to',
            'from',
            'to'
    )

    def capitalization_highlight(self, value):
        if value:
            words = value.split(' ')
            for i, word in enumerate(words):
                if i == 0 or i == (len(words) - 1):
                    continue
                if word.lower() in self.LOWERCASE_WORDS and not word.islower():
                    words[i] = "<strong>%s</strong>" % word
            return ' '.join(words)
        else:
            return value

    def render(self, name, value, attrs):
        attributes = attrs
        attributes['type'] = 'hidden'

        res = super(ContenteditableInput, self).render(name, value, attrs=attributes)

        val_escaped = escape(value)
        res += '<div class="vTextField contenteditable" data-target-input="#%s" contenteditable>%s</div>' % \
            (attrs['id'], self.capitalization_highlight(val_escaped))
        return res

    class Media:
        js = ('musicdb/contenteditable.widget.js',)
