# Generated by Django 5.0.12 on 2025-02-07 19:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0002_brunchreservation_brunch'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='name',
        ),
    ]
