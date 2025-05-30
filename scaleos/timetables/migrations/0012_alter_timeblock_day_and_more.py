# Generated by Django 5.0.12 on 2025-05-23 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetables', '0011_alter_timeblock_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeblock',
            name='day',
            field=models.CharField(choices=[('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday'), ('7_EVERY_DAY', 'every day'), ('8_EVERY_WEEKDAY', 'every weekday'), ('9_EVERY_WEEKEND', 'every weekend'), ('EVERY_PUBLIC_HOLIDAY', 'every public holiday')], default='0', max_length=50),
        ),
        migrations.AlterField(
            model_name='timetablepublicholiday',
            name='holiday_status',
            field=models.CharField(choices=[('OPEN_AS_USUAL', 'open as usual'), ('CLOSED', 'closed'), ('LIKE_EVERY_HOLIDAY', 'like every holiday'), ('SPECIAL_HOURS', 'special hours')], default='CLOSED', max_length=50),
        ),
    ]
