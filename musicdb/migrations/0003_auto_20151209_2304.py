# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicdb', '0002_auto_20151202_1900'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='path',
            field=models.FilePathField(recursive=True, allow_files=False, allow_folders=True, blank=True, path=b'/home/noname/musiclibtest', null=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='genre',
            field=models.ManyToManyField(to='musicdb.Genre', blank=True),
        ),
    ]
