from django.shortcuts import render
from django.views import View
import json
import pdb
from django.contrib.auth import authenticate
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dash.models import Wallet
from django.db.models import Q
from django.contrib.auth.models import User
from coinbase.wallet.client import Client
from .models import Rate
from django.conf import settings
from dash.functions import broadcast_eth_transaction, create_eth_transaction,create_transaction
from blockcypher import make_tx_signatures, broadcast_signed_transaction
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
    eth = get_wallet('eth', request.user)
    btc = get_wallet('btc', request.user)
    manna = get_wallet('MAN', request.user)
    rate=Rate.objects.get(id=1)
    try:
        eth_dollar=eth.main_balance/rate.eth
        eth_dollar=eth_dollar/settings.WEI
    except:
        eth_dollar=0
    try:
        btc_dollar=btc.main_balance/rate.btc
        btc_dollar = eth_dollar / settings.SATOSHI
    except:
        btc_dollar=0
    try:
        manna_dollar=manna.main_balance/rate.manna
    except:
        manna_dollar=0
    data={'wallets': [{'eth_balance':eth.main_balance,
                          'coin_symbol':eth.coin,
                          'id':eth.id,
                           'eth_dollar':eth_dollar,
                          'name':'Ethereum' },
                         {'btc_balance': btc.main_balance,
                          'coin_symbol': btc.coin,
                          'id': btc.id,
                          'btc_dollar':btc_dollar,
                          'name': 'Bitcoin'},
                         {'manna_balance': manna.main_balance,
                          'coin_symbol': manna.coin,
                          'id': btc.id,
                          'manna_dollar':manna_dollar,
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
            response['message']='Successful Account created for firstname'

    else:
        response['message'] = 'Email already exist'

    return JsonResponse(response)

@csrf_exempt
def WalletView(request, coin_symbol):
    wallet=get_wallet(coin_symbol,request.user)
    if coin_symbol == 'eth':
        try:
            balance=wallet.main_balance/settings.WEI
        except:
            balance=0
    if coin_symbol=='btc':
        try:
            balance = wallet.main_balance / settings.BTC
        except:
            balance = 0
    if coin_symbol=='MAN':
        balance=wallet.main_balance
    data={'balance': balance,
     'coin_symbol': wallet.coin,
     'id': wallet.id,
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
    payload = request.body.decode("utf-8")
    data = json.loads(payload)
    response = {'status': 400}
    coin=coin_symbol
    amount=data.get('amount')
    addr=data.get('address')
    wallet = get_wallet(coin_symbol, request.user)
    addresses = wallet.address_set.all()
    if coin == 'btc':
        amount = int(float(amount) * settings.BTC)
    if coin == 'eth':
        amount = int(float(amount) * settings.WEI)

    if coin == settings.ETH:
        in_addr = addresses[0].address
        tx = create_eth_transaction('1c58b7be11a43b19bdda8f0663ca1e44f4297b7b', addr, amount)

    else:
        tx = create_transaction(request.user.username, addr, amount, coin)
    if 'errors' in tx:
        response['message']='Insufficient Balance'
        return JsonResponse(response)
    str_tx = json.dumps(tx)

    pdb.set_trace()
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
        response['message'] = 'Insufficient Balance'
        return JsonResponse(response)

    response['message']='Transaction successfully created'
    response['status']=200
    response['tx_hash']=tx_hash
    return JsonResponse(response)







def get_dollar_value(eth_balance, btc_balance):
    cl=Client(settings.API_KEY, settings.API_SECRET)
    currencies = cl.get_exchange_rates(currency='USD')
    #btc_rate=int(currencies['BTC'])
    #eth_rate=int(currencies['ETH'])
    pdb.set_trace()






