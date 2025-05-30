# Generated by Django 5.0.12 on 2025-05-22 10:19

import autoslug.fields
import django.db.models.deletion
import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PublicHoliday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=100, verbose_name='name')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, null=True, populate_from='name', unique=True)),
                ('happening_on', models.DateField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TimeTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('countries', django_countries.fields.CountryField(default='BE', max_length=746, multiple=True)),
                ('is_exceptionally_closed', models.BooleanField(default=False)),
                ('is_always_open', models.BooleanField(default=False)),
                ('is_always_closed', models.BooleanField(default=False)),
                ('is_always_closed_on_public_holidays', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PublicHolidayTimeBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_time', models.TimeField(null=True)),
                ('to_time', models.TimeField(null=True)),
                ('date', models.DateField(null=True)),
                ('public_holiday', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='public_holiday_time_blocks', to='timetables.publicholiday')),
            ],
            options={
                'get_latest_by': 'from_time',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TimeBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_time', models.TimeField(null=True)),
                ('to_time', models.TimeField(null=True)),
                ('day', models.CharField(choices=[('A_MONDAY', 'Monday'), ('B_TUESDAY', 'Tuesday'), ('C_WEDNESDAY', 'Wednesday'), ('D_THURSDAY', 'Thursday'), ('E_FRIDAY', 'Friday'), ('F_SATURDAY', 'Saturday'), ('G_SUNDAY', 'Sunday'), ('H_EVERY_DAY', 'every day'), ('I_EVERY_WEEKDAY', 'every weekday'), ('J_EVERY_WEEKEND', 'every weekend'), ('K_EVERY_PUBLIC_HOLIDAY', 'every public holiday')], default='A_MONDAY', max_length=50)),
                ('from_time_table', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='time_blocks', to='timetables.timetable')),
            ],
            options={
                'ordering': ['day', 'from_time'],
            },
        ),
        migrations.AddField(
            model_name='publicholiday',
            name='timetable',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='public_holidays', to='timetables.timetable'),
        ),
    ]
