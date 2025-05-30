# Generated by Django 5.0.12 on 2025-03-18 13:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0011_remove_person_slug_alter_person_name'),
        ('organizations', '0019_alter_organizationowner_organization'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationEmployee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='organizations.organization')),
                ('person', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employers', to='hr.person')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
