# Generated by Django 2.0.5 on 2018-05-27 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='test_model',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.TextField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]