# Generated by Django 5.0.12 on 2025-02-07 19:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_brunchconcept_default_ending_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reception',
            fields=[
                ('singleevent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='events.singleevent')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('events.singleevent',),
        ),
    ]
