# Generated by Django 5.0.12 on 2025-04-24 10:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0032_remove_organizationemployee_organization_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationOwner',
            fields=[
                ('organizationmember_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='organizations.organizationmember')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('organizations.organizationmember',),
        ),
    ]
