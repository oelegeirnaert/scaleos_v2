# Generated by Django 5.0.12 on 2025-03-25 11:12

import django.db.models.deletion
import phonenumber_field.modelfields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0015_alter_person_mother_tongue'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonLanguage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(blank=True, choices=[('en', 'English'), ('nl', 'Nederlands'), ('fr', 'Français'), ('de', 'Deutsch')], default='', max_length=50, verbose_name='Language')),
                ('writing_score', models.IntegerField(blank=True, null=True, verbose_name='Writing Score')),
                ('reading_score', models.IntegerField(blank=True, null=True, verbose_name='Reading Score')),
                ('speaking_score', models.IntegerField(blank=True, null=True, verbose_name='Speaking Score')),
                ('understanding_score', models.IntegerField(blank=True, null=True, verbose_name='understanding_score')),
                ('person', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='languages', to='hr.person')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonTelephoneNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('telephone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('telephone_type', models.CharField(blank=True, choices=[('MOBILE', 'mobile'), ('HOME', 'home'), ('WORK', 'work')], default='', max_length=50, verbose_name='Telephone Type')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_modifications', to=settings.AUTH_USER_MODEL)),
                ('person', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='telephone_numbers', to='hr.person')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
