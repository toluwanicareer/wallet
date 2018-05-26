from django.db import models
from django.contrib.auth.models import User
from .functions import generate_address, create_or_update_online_wallet
from django.contrib import messages
import time
import pdb
# Create your models here.

class Wallet(models.Model):
    coin=models.CharField(max_length=100, choices=(('btc','btc'),('eth','Ether'), ('bcy', 'bcy')))
    balance=models.DecimalField(max_digits=100, decimal_places=8)
    owner=models.ForeignKey(User,on_delete=models.CASCADE)
    status=models.BooleanField(default=False)
    network=models.CharField(max_length=200, null=True, default='test')

    def __str__(self):
        return self.coin



class Address(models.Model):
    address=models.CharField(max_length=200, null=True)
    wallet=models.ForeignKey(Wallet, on_delete=models.CASCADE)
    private_key_wif=models.TextField(null=True)
    private_key_hex=models.TextField(null=True)
    public_key=models.TextField(null=True)
    created_date=models.DateTimeField(auto_now_add=True, null=True)
    balance=models.DecimalField(null=True, default=0, decimal_places=20, max_digits=100)

    def __str__(self):
        return self.wallet.coin+' Address'


    def set_up(self, username):
        try:
            address=generate_address(self.wallet.coin,self.wallet.network)
        except:
            return False

        try:
             self.private_key_wif=address['wif']
        except:
            pass

        self.private_key_hex=address['private']
        self.public_key=address['public']
        self.address=address['address']
        self.save()

        if self.wallet.coin == 'btc':
            status=create_or_update_online_wallet(self.wallet.status, self.address, username, self.wallet.coin)
            if status:
                self.wallet.status=True
                self.wallet.save()

        return True


class Transaction(models.Model):
    tx=models.CharField(max_length=200, null=True)
    status=models.CharField(max_length=200,null=True, choices=(('Pending','Pending'),('Confirmed', 'Confirmed')))
    data=models.TextField()


