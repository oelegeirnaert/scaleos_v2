# Generated by Django 5.0.12 on 2025-02-22 15:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0028_remove_pricehistory_current_price_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pricehistory',
            name='includes_vat',
        ),
    ]
