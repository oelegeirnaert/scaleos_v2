# Generated by Django 5.0.12 on 2025-02-13 19:56

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0007_person_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, null=True, populate_from='name', unique=True),
        ),
    ]
