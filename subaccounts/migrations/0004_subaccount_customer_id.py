# Generated by Django 4.2.6 on 2023-11-16 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subaccounts', '0003_alter_customuser_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='subaccount',
            name='customer_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]