# Generated by Django 5.0.12 on 2025-02-21 12:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0023_alter_agepricematrixitem_minimum_persons'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pricehistory',
            name='price',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='history', to='payments.price'),
        ),
    ]
