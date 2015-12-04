# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicdb', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='track',
            unique_together=set([('album', 'track_num', 'disc')]),
        ),
    ]
