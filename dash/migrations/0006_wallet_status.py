# Generated by Django 2.0.5 on 2018-05-19 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0005_address_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallet',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
