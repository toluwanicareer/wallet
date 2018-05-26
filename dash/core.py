from pybitcoin import BitcoinPrivateKey


def generate_address():

    context=dict()
    private_key = BitcoinPrivateKey()
    context['pr_hex'] = private_key.to_hex()
    context['pr_wif'] = private_key.to_wif()
    public_key=private_key.public_key()
    context['pu_hex'] = public_key.to_hex()
    context['address'] = public_key.address()
    return context





