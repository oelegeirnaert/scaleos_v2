# Generated by Django 5.0.12 on 2025-03-13 09:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0033_alter_concept_name_alter_event_name'),
        ('reservations', '0030_eventreservationsettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='reservation_settings',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='reservations.eventreservationsettings'),
        ),
    ]
