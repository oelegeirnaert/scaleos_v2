# Generated by Django 5.0.12 on 2025-03-31 07:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0075_remove_concept_event_reservation_payment_settings_and_more'),
        ('payments', '0084_alter_eventreservationpaymentcondition_event_reservation_payment_settings_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eventreservationpaymentsettings',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='eventreservationpaymentsettings',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='eventreservationpaymentsettings',
            name='organization',
        ),
        migrations.DeleteModel(
            name='EventReservationPaymentCondition',
        ),
        migrations.DeleteModel(
            name='EventReservationPaymentSettings',
        ),
    ]
