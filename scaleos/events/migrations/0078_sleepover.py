# Generated by Django 5.0.12 on 2025-04-02 12:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0077_alter_customerconcept_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SleepOver',
            fields=[
                ('singleevent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='events.singleevent')),
            ],
            options={
                'verbose_name': 'sleep over',
                'verbose_name_plural': 'sleep overs',
            },
            bases=('events.singleevent',),
        ),
    ]
