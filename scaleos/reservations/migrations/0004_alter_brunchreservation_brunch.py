# Generated by Django 5.0.12 on 2025-02-07 19:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_brunchconcept_default_ending_time'),
        ('reservations', '0003_remove_reservation_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brunchreservation',
            name='brunch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='events.brunchevent'),
        ),
    ]
