# Generated by Django 5.0.12 on 2025-04-17 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0027_alter_organizationcustomer_b2b'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
