# Generated by Django 5.0.12 on 2025-05-16 08:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buildings', '0003_floor_transition_durtion'),
    ]

    operations = [
        migrations.RenameField(
            model_name='floor',
            old_name='transition_durtion',
            new_name='transition_duration',
        ),
    ]
