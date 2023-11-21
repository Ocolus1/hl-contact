# Generated by Django 4.2.6 on 2023-11-19 19:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('subaccounts', '0004_subaccount_customer_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='CalendarDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bookingMethod', models.CharField(max_length=200)),
                ('days', models.JSONField(null=True)),
                ('timezone', models.CharField(max_length=200)),
                ('inspectionDuration', models.CharField(max_length=200)),
                ('timeBuffer', models.CharField(max_length=252)),
                ('appointmentReminder', models.CharField(max_length=252)),
                ('notificationPhoneNumber', models.CharField(blank=True, max_length=200, null=True)),
                ('notificationEmail', models.CharField(blank=True, max_length=200, null=True)),
                ('sub_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subaccounts.subaccount')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
