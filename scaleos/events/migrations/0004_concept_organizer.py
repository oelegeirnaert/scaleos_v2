# Generated by Django 5.0.12 on 2025-02-07 13:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_foodconcept_singleevent_event_name_delete_buffet'),
        ('organizations', '0003_remove_organization_registered_country_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='concept',
            name='organizer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='organizations.organization'),
        ),
    ]
