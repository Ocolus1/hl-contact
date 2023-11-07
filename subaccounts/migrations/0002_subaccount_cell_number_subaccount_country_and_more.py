# Generated by Django 4.2.6 on 2023-10-26 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subaccounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subaccount',
            name='cell_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='subaccount',
            name='country',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='subaccount',
            name='timezone',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
