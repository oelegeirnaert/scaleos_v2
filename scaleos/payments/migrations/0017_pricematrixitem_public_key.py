# Generated by Django 5.0.12 on 2025-02-17 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0016_alter_agepricematrixitem_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pricematrixitem',
            name='public_key',
            field=models.UUIDField(editable=False, null=True, unique=True),
        ),
    ]
