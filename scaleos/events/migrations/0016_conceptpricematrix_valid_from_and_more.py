# Generated by Django 5.0.12 on 2025-02-08 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0015_conceptpricematrix'),
    ]

    operations = [
        migrations.AddField(
            model_name='conceptpricematrix',
            name='valid_from',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conceptpricematrix',
            name='valid_till',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
