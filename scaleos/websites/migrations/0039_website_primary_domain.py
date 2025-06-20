# Generated by Django 5.0.12 on 2025-06-06 09:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websites', '0038_alter_website_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='website',
            name='primary_domain',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_for_website', to='websites.websitedomain'),
        ),
    ]
