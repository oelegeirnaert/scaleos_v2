# Generated by Django 5.0.12 on 2025-03-27 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0045_alter_price_vat_percentage_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentreservationsettings',
            name='only_when_group_exceeds',
            field=models.IntegerField(blank=True, help_text='number of persons', null=True),
        ),
    ]
