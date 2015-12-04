# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import musicdb.models
import django.utils.timezone
import django.core.files.storage
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('album_id', models.AutoField(serialize=False, editable=False, primary_key=True)),
                ('is_available', models.BooleanField(default=True)),
                ('add_time', models.DateTimeField(auto_now_add=True)),
                ('active_from', models.DateField(null=True, blank=True)),
                ('path', models.FilePathField(recursive=True, allow_files=False, allow_folders=True, blank=True, path=b'/home/noname/musiclibtest', null=True)),
                ('title', models.CharField(max_length=255, null=True, blank=True)),
                ('date', models.DateField()),
                ('release_date', models.DateField(null=True, blank=True)),
                ('catalog_num', models.CharField(max_length=256, null=True, blank=True)),
                ('barcode', models.CharField(max_length=256, null=True, blank=True)),
                ('source', models.PositiveSmallIntegerField(default=1, choices=[(0, 'my'), (1, 'what.cd'), (2, 'waffles.fm')])),
                ('source_id', models.CharField(max_length=256, null=True, blank=True)),
                ('release_type', models.PositiveSmallIntegerField(default=0, choices=[(0, 'LP'), (1, 'EP'), (2, 'Anthology'), (3, 'Soundtrack'), (4, 'Compilation'), (5, 'Single'), (6, 'Live')])),
                ('comment', models.TextField(null=True, blank=True)),
                ('edition_title', models.CharField(max_length=256, null=True, blank=True)),
                ('mbid', models.CharField(max_length=36, null=True, blank=True)),
                ('rg_peak', models.FloatField(null=True, editable=False, blank=True)),
                ('rg_gain', models.FloatField(null=True, editable=False, blank=True)),
            ],
            options={
                'ordering': ['artist'],
            },
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('artist_id', models.AutoField(serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Cover',
            fields=[
                ('cover_id', models.AutoField(serialize=False, editable=False, primary_key=True)),
                ('cover', models.ImageField(storage=django.core.files.storage.FileSystemStorage(base_url='/musicdb/media/', location=b'/home/noname/musiclibtest'), null=True, upload_to=musicdb.models.coverLocation, blank=True)),
                ('covertype', models.CharField(default='front_out', max_length=10, choices=[('back_out', 'back out'), ('front_out', 'front out'), ('back_in', 'back in'), ('front_in', 'front in'), ('disc', 'disc'), ('in', 'in'), ('out', 'out'), ('booklet', 'booklet')])),
                ('sort', models.PositiveSmallIntegerField(default=1)),
                ('album', models.ForeignKey(to='musicdb.Album')),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlayLog',
            fields=[
                ('play_log_id', models.AutoField(serialize=False, editable=False, primary_key=True)),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('source', models.PositiveSmallIntegerField(choices=[(0, '\u0414\u043e\u043c\u0430'), (1, '\u0421 \u043f\u043b\u0435\u0435\u0440\u0430')])),
            ],
            options={
                'ordering': ['-time'],
            },
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('track_id', models.AutoField(serialize=False, editable=False, primary_key=True)),
                ('track_num', models.PositiveSmallIntegerField()),
                ('title', models.CharField(max_length=255)),
                ('track_artist', models.CharField(max_length=255, null=True, blank=True)),
                ('length', models.PositiveIntegerField()),
                ('disc', models.PositiveSmallIntegerField(default=1)),
                ('uri', models.CharField(max_length=1024, null=True, blank=True)),
                ('lirycs', models.TextField(null=True, blank=True)),
                ('rg_peak', models.FloatField(null=True, blank=True)),
                ('rg_gain', models.FloatField(null=True, blank=True)),
                ('album', models.ForeignKey(to='musicdb.Album')),
            ],
        ),
        migrations.AddField(
            model_name='playlog',
            name='track',
            field=models.ForeignKey(to='musicdb.Track'),
        ),
        migrations.AddField(
            model_name='playlog',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='album',
            name='artist',
            field=models.ForeignKey(to='musicdb.Artist'),
        ),
        migrations.AddField(
            model_name='album',
            name='genre',
            field=models.ManyToManyField(to='musicdb.Genre', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='album',
            name='label',
            field=models.ForeignKey(blank=True, to='musicdb.Label', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='playlog',
            unique_together=set([('track', 'time', 'source')]),
        ),
        migrations.AlterUniqueTogether(
            name='cover',
            unique_together=set([('album', 'covertype', 'sort')]),
        ),
    ]
