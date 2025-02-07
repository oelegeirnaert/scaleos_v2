# Generated by Django 5.0.12 on 2025-02-07 22:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0013_bruncheventprice'),
    ]

    operations = [
        migrations.AddField(
            model_name='bruncheventprice',
            name='brunch_event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='events.brunchevent'),
        ),
    ]
