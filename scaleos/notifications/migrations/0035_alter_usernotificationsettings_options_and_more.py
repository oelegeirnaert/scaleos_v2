# Generated by Django 5.0.12 on 2025-04-17 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0034_usernotificationsettings_delete_notificationsettings'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usernotificationsettings',
            options={'verbose_name': 'user notification settings', 'verbose_name_plural': 'user notification settings'},
        ),
        migrations.AddField(
            model_name='notification',
            name='send_in_amount',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='send_in_interval',
            field=models.CharField(choices=[('seconds', 'seconds'), ('minutes', 'minutes'), ('hours', 'hour'), ('days', 'days'), ('weeks', 'weeks'), ('months', 'months'), ('years', 'years')], default='days', max_length=50),
        ),
    ]
