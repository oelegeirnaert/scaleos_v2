# Generated by Django 5.0.12 on 2025-02-07 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_agepricematrix_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='price',
            name='public_key',
            field=models.UUIDField(editable=False, null=True, unique=True),
        ),
    ]
