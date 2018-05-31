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
        eth = get_wallet('eth', user)
        btc = get_wallet('btc', user)
        manna = get_wallet('MAN', user)
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





def get_wallet(wallet, user):
    wallet = Wallet.objects.get(Q(owner=user), coin=wallet)
    return wallet

'''
 'wallets': [{'eth_balance':eth.main_balance,
                          'coin_symbol':eth.coin,
                          'id':eth.id,
                          'name':'Ethereum' },
                         {'btc_balance': btc.main_balance,
                          'coin_symbol': btc.coin,
                          'id': btc.id,
                          'name': 'Bitcoin'},
                         {'manna_balance': btc.main_balance,
                          'coin_symbol': btc.coin,
                          'id': btc.id,
                          'name': 'Manna'}
                         ]}
'''