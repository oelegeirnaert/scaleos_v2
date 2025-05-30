# Generated by Django 5.0.12 on 2025-05-05 10:51

import autoslug.fields
import colorfield.fields
import django.db.models.deletion
import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=100, verbose_name='name')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, null=True, populate_from='name', unique=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('show_name_on_website', models.BooleanField(default=True)),
                ('rotate', models.IntegerField(default=0)),
                ('margin_top', models.CharField(default='30px', help_text='with unit (ex: px, rem, em)')),
                ('background_color', colorfield.fields.ColorField(blank=True, default='#00000000', image_field=None, max_length=25, null=True, samples=None)),
                ('parent_block', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='websites.block')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=100, verbose_name='name')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, null=True, populate_from='name', unique=True)),
                ('ordering', models.PositiveIntegerField(db_index=True, default=0, verbose_name='ordering')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('show_in_menu', models.BooleanField(default=True)),
                ('show_in_footer_menu', models.BooleanField(default=True)),
                ('show_name_on_website', models.BooleanField(default=True)),
                ('menu_name', models.CharField(blank=True, default='')),
                ('slogan', models.CharField(blank=True, default='')),
                ('header_height', models.CharField(blank=True, default='500px;')),
                ('parent_page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='websites.page')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'page',
                'verbose_name_plural': 'pages',
                'ordering': ['ordering'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PageBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordering', models.PositiveIntegerField(db_index=True, default=0, verbose_name='ordering')),
                ('block', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='websites.block')),
                ('page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='websites.page')),
            ],
            options={
                'verbose_name': 'page block',
                'verbose_name_plural': 'page blocks',
                'ordering': ['ordering'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_key', models.UUIDField(editable=False, null=True, unique=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('domain_name', models.CharField(blank=True, default='')),
                ('slogan', models.CharField(blank=True, default='')),
                ('homepage', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='homepage', to='websites.page')),
                ('terms_and_conditions_page', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='terms_and_conditions', to='websites.page')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='page',
            name='website',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pages', to='websites.website'),
        ),
    ]
