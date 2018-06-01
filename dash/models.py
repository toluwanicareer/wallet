from django.db import models
from django.contrib.auth.models import User
from .functions import generate_address, create_or_update_online_wallet,create_eth_wallet,subscribe_to_webhook
from django.conf import settings
from django.contrib import messages
import time
import pdb
# Create your models here.

class Wallet(models.Model):
    coin=models.CharField(max_length=100, choices=(('btc','btc'),('eth','Ether'),('beth','BETH') ,
                                                   ('bcy', 'bcy'), ('MAN', 'Manna') ))
    main_balance=models.IntegerField(default=0)
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
    balance=models.IntegerField(default=0)

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
        try:
            subscribe_to_webhook(self.wallet.coin, self.wallet.network, self.address)
        except:
            return False
        self.save()
        status=False
        if self.wallet.coin == 'btc':
            status=create_or_update_online_wallet(self.wallet.status, self.address, username, self.wallet.coin)



        if status:
            self.wallet.status = True
            self.wallet.save()


        return self.address


class Transaction(models.Model):
    tx=models.CharField(max_length=200, null=True)
    wallet=models.ForeignKey(Wallet, on_delete=models.CASCADE, null=True)
    amount=models.IntegerField(null=True)
    hash=models.TextField(null=True)
    pay_in=models.BooleanField(default=False)

def tx_handler(tx_hash,input_list, output_list, total):
    try:
        tx=Transaction.objects.get(hash=tx_hash)
    except Transaction.DoesNotExist:
        addr=input_list[0]#get the first address
        try:
            addr=Address.objects.get(address=addr)
            wallet=addr.wallet
            wallet.main_balance=wallet.main_balance- int(total)
            #pdb.set_trace()
            wallet.save()
            tx = Transaction(hash=tx_hash, amount=int(total), pay_in=False, wallet=wallet)
            tx.save()
        except Address.DoesNotExist:
            pass

        addr = output_list[0]  # get the first address
        try:
            addr = Address.objects.get(address=addr)
            wallet = addr.wallet
            wallet.main_balance=wallet.main_balance + int(total)
            wallet.save()
            #pdb.set_trace()
            tx = Transaction(hash=tx_hash, amount=int(total), pay_in=True, wallet=wallet)
            tx.save()
        except Address.DoesNotExist:
            pass





