# Generated by Django 5.0.12 on 2025-02-08 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0010_remove_pricematrix_valid_from_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pricematrix',
            name='name',
            field=models.CharField(default='', max_length=100, verbose_name='name'),
        ),
    ]
