# Generated by Django 5.0.12 on 2025-02-08 08:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('payments', '0008_bulkpricematrix_bulkpricematrixitem'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agepricematrix',
            options={'base_manager_name': 'objects'},
        ),
        migrations.AlterModelOptions(
            name='bulkpricematrix',
            options={'base_manager_name': 'objects'},
        ),
        migrations.AlterModelOptions(
            name='pricematrix',
            options={'base_manager_name': 'objects'},
        ),
        migrations.AddField(
            model_name='pricematrix',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype'),
        ),
    ]
