# Generated by Django 5.0.12 on 2025-05-22 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetables', '0003_publicholiday_country_publicholiday_name_de_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicholiday',
            name='year',
            field=models.IntegerField(null=True),
        ),
    ]
