# Generated by Django 5.0.12 on 2025-02-08 17:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0019_alter_conceptpricematrix_concept'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='receptionevent',
            options={'verbose_name': 'reception event', 'verbose_name_plural': 'reception events'},
        ),
    ]
