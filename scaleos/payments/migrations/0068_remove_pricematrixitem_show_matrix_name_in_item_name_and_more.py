# Generated by Django 5.0.12 on 2025-03-28 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0067_pricematrixitem_show_matrix_name_in_item_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pricematrixitem',
            name='show_matrix_name_in_item_name',
        ),
        migrations.AddField(
            model_name='pricematrix',
            name='show_matrix_name_in_item_name',
            field=models.BooleanField(default=True),
        ),
    ]
