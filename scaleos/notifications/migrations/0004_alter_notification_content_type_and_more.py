# Generated by Django 5.0.12 on 2025-03-17 11:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('notifications', '0003_notificationsettings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='content_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='object_id',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
