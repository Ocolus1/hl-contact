# Generated by Django 4.2.6 on 2023-11-19 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subaccounts', '0006_calendardetails_notificationpreference'),
    ]

    operations = [
        migrations.AddField(
            model_name='calendardetails',
            name='email',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]