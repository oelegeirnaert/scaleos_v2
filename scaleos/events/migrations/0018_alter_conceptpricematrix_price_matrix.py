# Generated by Django 5.0.12 on 2025-02-08 10:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0017_alter_conceptpricematrix_concept'),
        ('payments', '0010_remove_pricematrix_valid_from_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conceptpricematrix',
            name='price_matrix',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='payments.pricematrix'),
        ),
    ]
