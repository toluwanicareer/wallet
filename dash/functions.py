import requests
from blockcypher import simple_spend, create_wallet_from_address, get_wallet_addresses, \
    add_address_to_wallet, create_unsigned_tx, simple_spend_p2sh,  make_tx_signatures
import time
from django.conf import settings
import pdb

#14tmXRFucqDG96SmhLRRYZtQzvH1b4zfCv

def generate_address(coin_symbol, network):
    url = 'https://api.blockcypher.com/v1/'+coin_symbol+'/'+network+'/addrs'
    response = requests.post(url)

    #print(response)
    return response.json()


def create_eth_transaction(input_addr, output_addr, value):
    url='https://api.blockcypher.com/v1/eth/main/txs/new?token='+settings.TOKEN
    tx={"inputs":
            [{"addresses":
                  [input_addr]}],
        "outputs":
            [{"addresses":
                  [output_addr], "value": value}]}
    response=requests.post(url, data=tx)
    pdb.set_trace()
    return response.json()


def create_transaction(username,addr,amount, coin_symbol):
    inputs = [{'wallet_name': username, 'wallet_token':settings.TOKEN}, ]
    outputs = [{'address': addr, 'value': amount}]
    unsigned_tx = create_unsigned_tx(inputs=inputs, outputs=outputs, coin_symbol=coin_symbol, preference='low')

    return unsigned_tx
'''
def create_transaction(all_from_public_key, from_priv_key,to_address,satoshis, coin_symbol, change_address):
    tx=simple_spend_p2sh(all_from_public_key, from_priv_key, to_address, satoshis,coin_symbol=coin_symbol,
                         api_key='993d49173a32400eba3aaafd8b94d336', change_address=change_address)
    pdb.set_trace()
    return tx
'''




def create_or_update_online_wallet(wallet_status, addr, username, coin_symbol):
    response=dict()
    #wallet=get_wallet_addresses(wallet_name=username, api_key='993d49173a32400eba3aaafd8b94d336', coin_symbol=coin_symbol)
    if  not wallet_status:
        try:
            create_wallet_from_address(wallet_name=username, address=addr, api_key=settings.TOKEN, coin_symbol=coin_symbol)
        except:
            time.sleep(30)
            create_wallet_from_address(wallet_name=username, address=addr, api_key=settings.TOKEN, coin_symbol=coin_symbol)
        status =True # which means wallet was just created
    else:
        try:
            ok=add_address_to_wallet(wallet_name=username, address=addr, api_key=settings.TOKEN, coin_symbol=coin_symbol)
        except:
            time.sleep(30)
            ok = add_address_to_wallet(wallet_name=username, address=addr, api_key=settings.TOKEN, coin_symbol=coin_symbol)
        status=False
    return status
















