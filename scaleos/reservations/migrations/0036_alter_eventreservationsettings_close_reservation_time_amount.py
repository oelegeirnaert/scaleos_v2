# Generated by Django 5.0.12 on 2025-03-20 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0035_rename_close_reservation_eventreservationsettings_close_reservation_time_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventreservationsettings',
            name='close_reservation_time_amount',
            field=models.IntegerField(blank=True, default=2, null=True),
        ),
    ]
