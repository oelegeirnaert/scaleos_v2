# Generated by Django 5.0.12 on 2025-02-08 08:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0006_remove_brunchreservation_brunch_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brunchreservation',
            name='age_price_matrix_item',
        ),
    ]
