# Generated by Django 5.0.12 on 2025-04-25 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0066_guestinvite_to_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='guestinvite',
            name='last_name',
        ),
        migrations.AddField(
            model_name='guestinvite',
            name='family_name',
            field=models.CharField(blank=True, default=''),
        ),
    ]
