# Generated by Django 5.0.12 on 2025-05-15 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0005_alter_basefile_file_alter_basefile_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='basefile',
            name='checksum',
            field=models.CharField(blank=True, editable=False, max_length=64),
        ),
    ]
