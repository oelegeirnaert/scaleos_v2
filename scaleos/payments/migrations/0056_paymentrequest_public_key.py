# Generated by Django 5.0.12 on 2025-03-27 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0055_alter_cashpaymentmethod_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentrequest',
            name='public_key',
            field=models.UUIDField(editable=False, null=True, unique=True),
        ),
    ]
