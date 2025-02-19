# Generated by Django 5.0.12 on 2025-02-19 14:41

import scaleos.shared.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0021_alter_reservation_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='card_description',
            field=models.TextField(default='', verbose_name='card description'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='card_image',
            field=models.ImageField(null=True, upload_to=scaleos.shared.models.CardModel.model_directory_path, verbose_name='card image'),
        ),
    ]
