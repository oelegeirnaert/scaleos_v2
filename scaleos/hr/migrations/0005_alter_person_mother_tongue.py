# Generated by Django 5.0.12 on 2025-02-08 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0004_alter_person_family_name_alter_person_gender_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='mother_tongue',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('fr-fr', 'French'), ('nl', 'Dutch')], default='', max_length=50),
        ),
    ]
