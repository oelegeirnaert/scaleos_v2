# Generated by Django 5.0.12 on 2025-05-21 19:19

import scaleos.shared.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catering', '0018_catering_public_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='card_description',
            field=models.TextField(blank=True, default='', verbose_name='card description'),
        ),
        migrations.AddField(
            model_name='product',
            name='card_image',
            field=models.ImageField(blank=True, null=True, upload_to=scaleos.shared.models.CardModel.model_directory_path, verbose_name='card image'),
        ),
        migrations.AddField(
            model_name='product',
            name='transition',
            field=models.CharField(choices=[('fade', 'Fade'), ('slide', 'Slide'), ('zoom', 'Zoom'), ('flip', 'Flip')], default='fade', max_length=50, verbose_name='every interval'),
        ),
        migrations.AddField(
            model_name='product',
            name='transition_duration',
            field=models.IntegerField(default=1500, help_text='in milliseconds', verbose_name='transition duration'),
        ),
        migrations.AddField(
            model_name='product',
            name='transition_interval',
            field=models.IntegerField(default=5000, help_text='in milliseconds', verbose_name='transition interval'),
        ),
    ]
