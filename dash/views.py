from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import  Wallet, Address, Transaction
from django.http import Http404, HttpResponseRedirect
from django.db.models import Q
from .functions import create_transaction, create_eth_transaction,broadcast_eth_transaction
import pdb
from django.conf import settings
from django.contrib import messages
from blockcypher import make_tx_signatures, broadcast_signed_transaction, subscribe_to_address_webhook
import json
# Create your views here.



class WalletView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        coin_symbol=kwargs.pop('coin_symbol')
        try:
            wallet=Wallet.objects.get(Q(owner=request.user), coin=coin_symbol)
            balance=wallet.main_balance
            coin_balance=balance/settings.WEI
        except Wallet.DoesNotExist:
            raise Http404()
        addr=Address.objects.filter(wallet=wallet)


        return render(request, 'wallet_admin/wallet.html', {'addr':addr,'coin_symbol':coin_symbol,
                                                            'balance':balance, 'coin_balance':coin_balance})

class generate_address(LoginRequiredMixin, View):

    def get(self,request, *args, **kwargs):
        coin_symbol=request.GET.get('coin_symbol')
        wallet = Wallet.objects.get(Q(owner=request.user), coin=coin_symbol)
        #if wallet.coin == 'eth' or wallet.coin == 'beth':
            #eth_address=wallet.address_set.all()
            #if eth_address.exists():
            #messages.warning(request, 'You can only manage one wallet address in ETH')
            #return HttpResponseRedirect('/office/wallet/'+coin_symbol+'/')
        addr=Address(wallet=wallet)

        addr=addr.set_up(request.user.username)
        if addr:
            messages.success(request, 'Address created succeefully')
        else:
            messages.warning(request, "Network Error")

        return HttpResponseRedirect('/office/wallet/'+coin_symbol+'/')


class receive_coin(LoginRequiredMixin, View):

    def get(self,request, *args, **kwargs):
        address_id=request.GET.get('addr_id')
        address=Address.objects.get(id=address_id)

        return render(request,'wallet_admin/receive.html', {'address':address.address})


class send_coin(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        coin=request.GET.get('coin_symbol')
        return render(request, 'wallet_admin/send.html', {'coin_symbol': coin})

    def post(self, request, *args, **kwargs):
        amount=request.POST.get('amount')
        addr=request.POST.get('address')
        coin=request.POST.get('coin_symbol')
        wallet = Wallet.objects.get(Q(owner=request.user), coin=coin)
        addresses=wallet.address_set.all()
        if coin =='btc':
            amount=int(float(amount)*100000000)
        else:
            amount=int(float(amount)*settings.WEI)

        if coin == settings.ETH:
            in_addr=addresses[0].address
            tx=create_eth_transaction('f814981e49d8fc2c42c43143a575aeec4b000c34', addr, amount)

        else:
            tx=create_transaction(request.user.username, addr, amount,coin)
        if 'errors' in tx:
            messages.warning(request, 'Insufficient Balance ')
            return HttpResponseRedirect('/office/wallet/' + coin + '/')
        str_tx=json.dumps(tx)

        pdb.set_trace()
        try:
            inputs=tx['tx']['inputs'][0]['addresses']
        except :
            messages.warning(request, 'Insufficient Balance ')
            return HttpResponseRedirect('/office/')

        input_addr=addresses.filter(address__in=inputs)
        public_key=[addr.public_key for addr in input_addr ]
        priv_key=[addr.private_key_hex for addr in input_addr]
        #pdb.set_trace()
        signatures = make_tx_signatures(txs_to_sign=tx['tosign'], privkey_list=priv_key,
                                           pubkey_list=public_key)

        if coin == settings.ETH:
            tx_hash=broadcast_eth_transaction(tx,signatures,public_key)
        else:
            tx_hash=broadcast_signed_transaction(unsigned_tx=tx, signatures=signatures, pubkeys=public_key, api_key=settings.TOKEN)

        if 'errors' in tx_hash:
            messages.warning(request, 'Insufficient Balance ')
            return HttpResponseRedirect('/office/wallet/' + coin + '/')

        messages.success(request, 'Transaction successfully created')
        #create_transaction(from_public_key, from_priv_key,addr,amount,coin,change_address.address)
        return HttpResponseRedirect('/office/wallet/' + coin + '/')















def get_balance(wallet):
    return 0.002




