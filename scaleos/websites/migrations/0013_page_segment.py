# Generated by Django 5.0.12 on 2025-05-06 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websites', '0012_eventsblock'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='segment',
            field=models.CharField(choices=[('B2B', 'b2b'), ('B2C', 'b2c'), ('BOTH', 'both')], default='BOTH', max_length=50, verbose_name='segment'),
        ),
    ]
