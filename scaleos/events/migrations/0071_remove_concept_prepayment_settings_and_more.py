# Generated by Django 5.0.12 on 2025-03-29 08:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0070_concept_prepayment_settings_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='concept',
            name='prepayment_settings',
        ),
        migrations.RemoveField(
            model_name='event',
            name='prepayment_settings',
        ),
    ]
