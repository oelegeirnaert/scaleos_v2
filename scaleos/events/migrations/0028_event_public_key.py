# Generated by Django 5.0.12 on 2025-02-15 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0027_concept_public_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='public_key',
            field=models.UUIDField(editable=False, null=True, unique=True),
        ),
    ]
