# Generated by Django 5.0.12 on 2025-02-08 10:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0018_alter_conceptpricematrix_price_matrix'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conceptpricematrix',
            name='concept',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='events.concept'),
        ),
    ]
