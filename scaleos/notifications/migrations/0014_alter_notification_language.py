# Generated by Django 5.0.12 on 2025-03-20 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0013_alter_notification_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='language',
            field=models.CharField(blank=True, choices=[('en', '%s - %s'), ('fr', 'French'), ('nl', 'Dutch')], default='', max_length=50),
        ),
    ]
