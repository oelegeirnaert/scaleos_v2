# Generated by Django 5.0.12 on 2025-04-30 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0054_alter_notification_redirect_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='redirect_url',
            field=models.URLField(blank=True, default='', max_length=300, null=True),
        ),
    ]
