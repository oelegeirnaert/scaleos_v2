# Generated by Django 5.0.12 on 2025-04-22 13:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geography', '0012_terrace'),
        ('hr', '0020_alter_person_mother_tongue_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personaddress',
            name='address',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='geography.address', verbose_name='address'),
        ),
        migrations.AlterField(
            model_name='personaddress',
            name='person',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='hr.person', verbose_name='person'),
        ),
    ]
