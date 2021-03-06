# Generated by Django 2.0.5 on 2018-05-27 11:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=200, null=True)),
                ('private_key_wif', models.TextField(null=True)),
                ('private_key_hex', models.TextField(null=True)),
                ('public_key', models.TextField(null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('main_balance', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tx', models.CharField(max_length=200, null=True)),
                ('amount', models.IntegerField(null=True)),
                ('hash', models.TextField(null=True)),
                ('pay_in', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coin', models.CharField(choices=[('btc', 'btc'), ('eth', 'Ether'), ('beth', 'BETH'), ('bcy', 'bcy')], max_length=100)),
                ('balance', models.DecimalField(decimal_places=8, max_digits=100)),
                ('status', models.BooleanField(default=False)),
                ('network', models.CharField(default='test', max_length=200, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='transaction',
            name='wallet',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dash.Wallet'),
        ),
        migrations.AddField(
            model_name='address',
            name='wallet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dash.Wallet'),
        ),
    ]
