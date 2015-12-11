# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicdb', '0003_auto_20151209_2304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='track',
            name='path',
            field=models.FilePathField(null=True, recursive=True, blank=True, path=b'/home/noname/musiclibtest', unique=True, match='.*\\.flac$'),
        ),
    ]
