# Generated by Django 5.0.12 on 2025-05-20 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catering', '0006_alter_allergen_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allergen',
            name='name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
