# Generated by Django 5.0.12 on 2025-02-07 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_breakevent_brunchevent_ceremonyevent_closingevent_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='brunchconcept',
            name='default_starting_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
