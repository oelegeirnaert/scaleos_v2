# Generated by Django 5.0.12 on 2025-03-25 10:23

import django.db.models.deletion
import scaleos.shared.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geography', '0007_room_floor_public_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('floor_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='geography.floor')),
            ],
            options={
                'verbose_name': 'building',
                'verbose_name_plural': 'buildings',
            },
            bases=('geography.floor',),
        ),
        migrations.AlterModelOptions(
            name='floor',
            options={'verbose_name': 'floor', 'verbose_name_plural': 'floors'},
        ),
        migrations.AlterModelOptions(
            name='room',
            options={'verbose_name': 'room', 'verbose_name_plural': 'rooms'},
        ),
        migrations.AddField(
            model_name='floor',
            name='card_description',
            field=models.TextField(blank=True, default='', verbose_name='card description'),
        ),
        migrations.AddField(
            model_name='floor',
            name='card_image',
            field=models.ImageField(blank=True, null=True, upload_to=scaleos.shared.models.CardModel.model_directory_path, verbose_name='card image'),
        ),
        migrations.AddField(
            model_name='room',
            name='in_building',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='geography.building', verbose_name='in building'),
        ),
    ]
