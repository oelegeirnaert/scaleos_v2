# Generated by Django 5.0.12 on 2025-02-07 12:11

import django.db.models.deletion
import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0002_organization_registered_country_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='registered_country',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='registration_id',
        ),
        migrations.CreateModel(
            name='Enterprise',
            fields=[
                ('organization_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='organizations.organization')),
                ('registered_country', django_countries.fields.CountryField(default='BE', max_length=2, null=True)),
                ('registration_id', models.CharField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'enterprise',
                'verbose_name_plural': 'enterprises',
            },
            bases=('organizations.organization',),
        ),
    ]
