from django.shortcuts import render
from django.views import View
import json
import pdb
from django.contrib.auth import authenticate
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dash.models import Wallet, Transaction
from django.db.models import Q
from django.contrib.auth.models import User
from coinbase.wallet.client import Client
from .models import Rate
from django.conf import settings
from dash.functions import broadcast_eth_transaction, create_eth_transaction,create_transaction
from blockcypher import make_tx_signatures, broadcast_signed_transaction
from dash.models import Address
import requests


# Create your views here.
@csrf_exempt
def LoginView(request):

    payload = request.body.decode("utf-8")
    response = {'status': 400}

    try:
        login_data = json.loads(payload)

    except:
        response['message'] = 'Type error'
        #the dat is not in not in json
    username=login_data.get('username')
    password=login_data.get('password')
    user=authenticate(request,username=username, password=password)

    if user:

        #data = serializers.serialize('json', user, fields=('first_name', 'last_name', 'username', 'id'))
        data={'username':user.username, 'first_name':user.first_name,
              'last_name':user.first_name, 'id':user.pk,'email':user.email}

        response['status']=200
        response['message']='Successful Login'
        response['data']=data

    else:
        response['message']='Invalid Login'
        response['status'] = 401

    return JsonResponse(response)

def dash(request):

    id=request.GET.get('id')
    user=User.objects.get(id=id)
    eth = get_wallet(settings.ETH, user)
    btc = get_wallet(settings.BTC, user)
    manna = get_wallet('MAN', user)
    rate=Rate.objects.get(id=1)
    try:
        eth_dollar=eth.main_balance/rate.eth
        eth_dollar=eth_dollar/settings.WEI
        eth_dollar = round(eth_dollar, 2)
    except:
        eth_dollar='0'
    try:
        btc_dollar=btc.main_balance/rate.btc
        btc_dollar =btc_dollar / settings.SATOSHI
        btc_dollar=round(btc_dollar,2)
    except:
        btc_dollar='0'
    try:
        manna_dollar=manna.main_balance/rate.manna
    except:
        manna_dollar='0'
        #remember to do shit with zeros
    data={'status':200,
          'message':'Successful',
          'wallets': [{'balance':eth.main_balance,
                          'coin_symbol':eth.coin,
                          'id':eth.id,
                           'dollar':eth_dollar,
                          'name':'Ethereum' },
                         {'balance': btc.main_balance,
                          'coin_symbol': btc.coin,
                          'id': btc.id,
                          'dollar':btc_dollar,
                          'name': 'Bitcoin'},
                         {'balance': manna.main_balance,
                          'coin_symbol': manna.coin,
                          'id': btc.id,
                          'dollar':manna_dollar,
                          'name': 'Manna'}
                         ]}
    return JsonResponse(data)

@csrf_exempt
def signupView(request):
    payload = request.body.decode("utf-8")
    data = json.loads(payload)
    response = {'status': 400}
    username=data.get('username')
    firstname=data.get('firstname')
    lastname=data.get('lastname')
    password=data.get('password')
    email=data.get('email')
    status=chk_email(email)
    if status:# email does not exist
        try:
            user=User.objects.get(username=username)

            response['message'] = 'Username already exist'
        except User.DoesNotExist:

            #create user
            user=User.objects.create_user(username=username, is_active=True,password=password,
                                          first_name=firstname, last_name=lastname, email=email)
            response['status']=200
            wallet=Wallet(coin='btc', main_balance=0,owner=user, network='main')
            wallet.save()
            wallet = Wallet(coin='eth', main_balance=0, owner=user, network='main')
            wallet.save()
            wallet = Wallet(coin='MAN', main_balance=0, owner=user, network='main')
            wallet.save()
            response['message']='Successful Account created for firstname'

    else:
        response['message'] = 'Email already exist'

    return JsonResponse(response)
@csrf_exempt
def WalletView(request, coin_symbol):
    rate = Rate.objects.get(id=1)
    user=get_user(request)
    wallet=get_wallet(coin_symbol,user)
    transactions = list(Transaction.objects.only('hash','amount').filter(wallet=wallet).values()[:4])
    #data = serializers.serialize("json", transactions, fields=('hash', 'amount', 'payin'))

    #pdb.set_trace() 
    if coin_symbol ==settings.ETH:
        try:
            balance=wallet.main_balance/settings.WEI
            balance=round(balance,2)
            #pdb.set_trace()
            dollar=str(round((balance)/float(rate.eth), 2))

        except:
            balance='0'
            dollar='0'
    if coin_symbol==settings.BTC:
        try:
            balance = wallet.main_balance / settings.BTC
            balance = round(balance, 2)
            dollar=str(round(balance/float(rate.eth),2))
        except:
            balance = '0'
            dollar ='0'
    if coin_symbol=='MAN':
        balance=wallet.main_balance
        dollar='0'
    data={'balance': balance,
     'coin_symbol': wallet.coin,
     'id': wallet.id,
      'dollar':dollar,
      'transactions':transactions,
          'status':200,
          'message':'Successful'
 }
    return JsonResponse(data)

def get_wallet(wallet, user):
    wallet = Wallet.objects.get(Q(owner=user), coin=wallet)
    return wallet

def chk_email(email):
    user=User.objects.filter(email=email)
    if user.exists():
        return False
    else:
        return True


@csrf_exempt
def send_coin(request,coin_symbol):
    #user=get_user(request)
    payload = request.body.decode("utf-8")
    data = json.loads(payload)
    response = {'status': 400}
    coin=coin_symbol
    amount=data.get('amount')
    addr=data.get('address')
    id=data.get('id')
    user = User.objects.get(id=id)
    wallet = get_wallet(coin_symbol, user)
    addresses = wallet.address_set.all()
    if coin == settings.BTC:
        amount = int(float(amount) * settings.BTC)
        amount = int(float(amount) * settings.BTC)
    if coin == settings.ETH:
        amount = int(float(amount) * settings.WEI)

    if coin == settings.ETH:
        in_addr = addresses[0].address
        tx = create_eth_transaction(in_addr, addr, amount)

    else:
        tx = create_transaction(request.user.username, addr, amount, coin)
    if 'errors' in tx:
        response['message']='Insufficient Balance'
        return JsonResponse(response)
    str_tx = json.dumps(tx)

    try:
        inputs = tx['tx']['inputs'][0]['addresses']
    except:
        response['message'] = 'Insufficient Balance'
        return JsonResponse(response)
    input_addr = addresses.filter(address__in=inputs)
    public_key = [addr.public_key for addr in input_addr]
    priv_key = [addr.private_key_hex for addr in input_addr]
    # pdb.set_trace()
    signatures = make_tx_signatures(txs_to_sign=tx['tosign'], privkey_list=priv_key,
                                    pubkey_list=public_key)

    if coin == settings.ETH:
        tx_hash = broadcast_eth_transaction(tx, signatures, public_key)
    else:
        tx_hash = broadcast_signed_transaction(unsigned_tx=tx, signatures=signatures, pubkeys=public_key,
                                               api_key=settings.TOKEN)

    if 'errors' in tx_hash:
        pdb.set_trace()
        response['message'] = 'Insufficient Balance'
        return JsonResponse(response)

    response['message']='Transaction successfully created'
    response['status']=200
    response['tx_hash']=tx_hash
    return JsonResponse(response)

def receive_coin(request, coin_symbol):
    response={'status':400}
    user=get_user(request)
    wallet = get_wallet(coin_symbol, user)
    if coin_symbol== settings.BTC:

        addr = Address(wallet=wallet)
        addr = addr.set_up(user.username)
        if addr:
            response['message']='Address created successfully'
            response['status']=200
            response['data']={'address':addr}
        else:
            addr = wallet.address_set.all()
            if addr.exists():
                addr = addr[0].address
                response['status'] = 200
                response['data'] = {'address': addr}
                response['message'] = 'Address created successfully'
            else:
                response['message'] = 'Network Error'
    if coin_symbol==settings.ETH:
        addr=wallet.address_set.all()
        if addr.exists():
            addr = addr[0].address
            response['status'] = 200
            response['data'] = {'address': addr}
            response['message'] = 'Address created successfully'
        else:
            addr = Address(wallet=wallet)
            addr = addr.set_up(user.username)
            if addr:
                response['message'] = 'Address created successfully'
                response['status'] = 200
                response['data'] = {'address': addr}
            else:
                response['message'] = 'Network Error'




    return JsonResponse(response)



def get_dollar_value(eth_balance, btc_balance):
    cl=Client(settings.API_KEY, settings.API_SECRET)
    currencies = cl.get_exchange_rates(currency='USD')
    #btc_rate=int(currencies['BTC'])
    #eth_rate=int(currencies['ETH'])
    pdb.set_trace()


def get_user(req):
    id = req.GET.get('id')
    user = User.objects.get(id=id)
    return user



