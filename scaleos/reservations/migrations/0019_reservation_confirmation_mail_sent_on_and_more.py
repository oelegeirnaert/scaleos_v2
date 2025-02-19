# Generated by Django 5.0.12 on 2025-02-18 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0018_alter_reservation_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='confirmation_mail_sent_on',
            field=models.DateTimeField(blank=True, help_text='the moment the confirmation email of the reservation has been sent', null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='email_address_confirmed_on',
            field=models.DateTimeField(blank=True, help_text='the moment the user has clicked the confirmation button in the mail', null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='confirmed_on',
            field=models.DateTimeField(blank=True, help_text='the moment the employee has confirmed the reservation', null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='finished_on',
            field=models.DateTimeField(blank=True, help_text='the moment the reservation has been made.', null=True),
        ),
    ]
