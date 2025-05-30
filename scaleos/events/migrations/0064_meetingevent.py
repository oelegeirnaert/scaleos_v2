# Generated by Django 5.0.12 on 2025-03-26 08:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0063_presentationevent'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeetingEvent',
            fields=[
                ('singleevent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='events.singleevent')),
            ],
            options={
                'verbose_name': 'meeting',
                'verbose_name_plural': 'meetings',
            },
            bases=('events.singleevent',),
        ),
    ]
