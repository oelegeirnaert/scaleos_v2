# Generated by Django 5.0.12 on 2025-03-20 10:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0041_pricematrixitem_name_en_pricematrixitem_name_fr_fr_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pricematrixitem',
            old_name='name_fr_fr',
            new_name='name_fr',
        ),
    ]
