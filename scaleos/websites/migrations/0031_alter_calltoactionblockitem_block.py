# Generated by Django 5.0.12 on 2025-05-19 10:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websites', '0030_alter_calltoactionblockitem_block_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calltoactionblockitem',
            name='block',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='call_to_actions', to='websites.block'),
        ),
    ]
