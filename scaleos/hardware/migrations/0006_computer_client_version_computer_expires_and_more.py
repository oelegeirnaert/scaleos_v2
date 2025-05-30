# Generated by Django 5.0.12 on 2025-03-28 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hardware', '0005_network'),
    ]

    operations = [
        migrations.AddField(
            model_name='computer',
            name='client_version',
            field=models.CharField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='computer',
            name='expires',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='computer',
            name='hostname',
            field=models.CharField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='computer',
            name='ip_addresses',
            field=models.CharField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='computer',
            name='last_seen',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='computer',
            name='node_id',
            field=models.CharField(editable=False, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='computer',
            name='tailscale_ipv4',
            field=models.GenericIPAddressField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='computer',
            name='update_available',
            field=models.BooleanField(default=False),
        ),
    ]
