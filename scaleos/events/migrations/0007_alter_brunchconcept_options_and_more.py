# Generated by Django 5.0.12 on 2025-02-07 14:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_brunchconcept_dinneranddanceconcept_weddingconcept_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='brunchconcept',
            options={'verbose_name': 'brunch concept', 'verbose_name_plural': 'brunch concepts'},
        ),
        migrations.AlterModelOptions(
            name='dinneranddanceconcept',
            options={'verbose_name': 'dinner & dance concept', 'verbose_name_plural': 'dinner & dance concepts'},
        ),
        migrations.AlterModelOptions(
            name='weddingconcept',
            options={'verbose_name': 'wedding concept', 'verbose_name_plural': 'wedding concepts'},
        ),
    ]
