# Generated by Django 5.0.12 on 2025-05-16 08:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0102_concept_transition_durtion_event_transition_durtion'),
    ]

    operations = [
        migrations.RenameField(
            model_name='concept',
            old_name='transition_durtion',
            new_name='transition_duration',
        ),
        migrations.RenameField(
            model_name='event',
            old_name='transition_durtion',
            new_name='transition_duration',
        ),
    ]
