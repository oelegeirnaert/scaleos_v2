# Generated by Django 5.0.12 on 2025-04-16 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0050_invalidreservation'),
    ]

    operations = [
        migrations.AddField(
            model_name='invalidreservation',
            name='additional_info',
            field=models.TextField(blank=True, default='', verbose_name='additional info'),
        ),
        migrations.AlterField(
            model_name='invalidreservation',
            name='reason',
            field=models.CharField(choices=[('INVALID_EMAIL', 'invalid email'), ('NO_ACTIVE_ORGANIZATION', 'no active organization'), ('UNKNOWN', 'unknown')], default='UNKNOWN', max_length=50, null=True, verbose_name='reason'),
        ),
    ]
