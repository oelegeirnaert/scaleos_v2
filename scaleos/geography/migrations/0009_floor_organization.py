# Generated by Django 5.0.12 on 2025-03-25 10:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geography', '0008_building_alter_floor_options_alter_room_options_and_more'),
        ('organizations', '0020_organizationemployee'),
    ]

    operations = [
        migrations.AddField(
            model_name='floor',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organizations.organization', verbose_name='organization'),
        ),
    ]
