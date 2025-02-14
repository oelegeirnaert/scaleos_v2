# Generated by Django 5.0.12 on 2025-02-07 13:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_break_brunch_ceremony_closing_dance_dinner_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrunchConcept',
            fields=[
                ('concept_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='events.concept')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('events.concept',),
        ),
        migrations.CreateModel(
            name='DinnerAndDanceConcept',
            fields=[
                ('concept_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='events.concept')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('events.concept',),
        ),
        migrations.CreateModel(
            name='WeddingConcept',
            fields=[
                ('concept_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='events.concept')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('events.concept',),
        ),
        migrations.RemoveField(
            model_name='wedding',
            name='concept_ptr',
        ),
        migrations.DeleteModel(
            name='DinnerAndDance',
        ),
        migrations.DeleteModel(
            name='Wedding',
        ),
    ]
