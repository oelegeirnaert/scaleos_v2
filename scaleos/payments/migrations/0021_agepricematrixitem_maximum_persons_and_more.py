# Generated by Django 5.0.12 on 2025-02-21 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0020_alter_price_created_by_alter_pricehistory_created_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='agepricematrixitem',
            name='maximum_persons',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='agepricematrixitem',
            name='minimum_persons',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
