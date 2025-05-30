# Generated by Django 5.0.12 on 2025-05-20 07:29

import autoslug.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Caterer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=100, verbose_name='name')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, null=True, populate_from='name', unique=True)),
                ('public_key', models.UUIDField(editable=False, null=True, unique=True)),
                ('segment', models.CharField(choices=[('B2B', 'b2b'), ('B2C', 'b2c'), ('BOTH', 'both')], default='BOTH', max_length=50, verbose_name='segment')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
