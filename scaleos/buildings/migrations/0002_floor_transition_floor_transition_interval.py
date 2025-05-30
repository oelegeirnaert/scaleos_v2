# Generated by Django 5.0.12 on 2025-05-16 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buildings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='floor',
            name='transition',
            field=models.CharField(choices=[('fade', 'Fade'), ('slide', 'Slide'), ('zoom', 'Zoom'), ('flip', 'Flip')], default='fade', max_length=50, verbose_name='every interval'),
        ),
        migrations.AddField(
            model_name='floor',
            name='transition_interval',
            field=models.IntegerField(default=5000, help_text='in milliseconds', verbose_name='transition interval'),
        ),
    ]
