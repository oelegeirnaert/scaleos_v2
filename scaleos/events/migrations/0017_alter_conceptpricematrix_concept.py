# Generated by Django 5.0.12 on 2025-02-08 10:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0016_conceptpricematrix_valid_from_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conceptpricematrix',
            name='concept',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to='events.concept'),
        ),
    ]
