# Generated by Django 5.0.12 on 2025-02-13 19:56

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0007_enterprise_gps_point'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, null=True, populate_from='name', unique=True),
        ),
    ]
