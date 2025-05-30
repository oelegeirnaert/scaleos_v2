# Generated by Django 5.0.12 on 2025-02-26 12:46

import scaleos.shared.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0010_alter_organizationowner_person'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='card_description',
            field=models.TextField(default='', verbose_name='card description'),
        ),
        migrations.AddField(
            model_name='organization',
            name='card_image',
            field=models.ImageField(null=True, upload_to=scaleos.shared.models.CardModel.model_directory_path, verbose_name='card image'),
        ),
    ]
