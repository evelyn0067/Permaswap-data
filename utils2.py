from decimal import Decimal
import requests, json, urllib
from urllib.parse import urlencode, quote_plus
from data import *
from websocket import create_connection

HALF = Decimal('0.5')
router = 'wss://router.permaswap.network'
pay = 'https://api.everpay.io'

def liquidity_to_amount(liquidity, lower_price, upper_price, current_price):
    liquidity = Decimal(str(liquidity))
    lower_price = Decimal(str(lower_price))
    upper_price = Decimal(str(upper_price))
    current_price = Decimal(str(current_price))
    
    if lower_price >= current_price:
        x_amount = liquidity * (1/lower_price**HALF - 1/upper_price**HALF)
        y_amount = 0
    elif upper_price <= current_price:
        x_amount = 0
        y_amount = liquidity * (upper_price**HALF - lower_price**HALF)
    else:
        x_amount = liquidity * (1/current_price**HALF - 1/upper_price**HALF)
        y_amount = liquidity * (current_price**HALF - lower_price**HALF)

    return x_amount, y_amount

def liquidity_to_amount2(liquidity, lower_sqrt_price, upper_sqrt_price, current_sqrt_price):
    liquidity = Decimal(str(liquidity))
    lower_sqrt_price = Decimal(str(lower_sqrt_price))
    upper_sqrt_price = Decimal(str(upper_sqrt_price))
    current_sqrt_price = Decimal(str(current_sqrt_price))
    
    if lower_sqrt_price >= current_sqrt_price:
        x_amount = liquidity * (1/lower_sqrt_price - 1/upper_sqrt_price)
        y_amount = 0
    elif upper_sqrt_price <= current_sqrt_price:
        x_amount = 0
        y_amount = liquidity * (upper_sqrt_price - lower_sqrt_price)
    else:
        x_amount = liquidity * (1/current_sqrt_price - 1/upper_sqrt_price)
        y_amount = liquidity * (current_sqrt_price - lower_sqrt_price)

    return x_amount, y_amount

def get_liquidity(x_amount, y_amount):
    return (Decimal(x_amount) * Decimal(y_amount)) ** HALF

def get_price_from_redstone(token, currency, timestamp=''):
    '''eg:get_price_from_redstone('ar', 'usdt', 1642318120000)'''
    base_url = 'https://api.redstone.finance/prices'
    payload = {
        'symbols':'%s,%s'%(token.upper(), currency.upper()),
        'provider': 'redstone'
    }
    if timestamp:
        payload['toTimestamp'] = str(timestamp)

    url = '%s/?%s'%(base_url, urlencode(payload, quote_via=quote_plus))
    result = requests.get(url).json()
    price = result[token.upper()]['value']/result[currency.upper()]['value']
    return price

def get_price_from_ps(token, amount_in, decimals=4):
    order = get_order(pay, router, '0x61EbF673c200646236B2c53465bcA0699455d5FA', token, 'usdc', amount_in)
    #rate = int(float(order['rate']) * 10**(decimals))/10**(decimals)
    return order.get('rate', '') 

def get_amount_out(user, order, token_out_tag):
    amount_out = 0
    for path in order['paths']:
        if path['to'].lower() == user.lower() and path['tokenTag'] == token_out_tag:
            amount_out += int(path['amount'])
    return str(amount_out)

def get_order(pay_host, ps_router_host, address, token_in, token_out, amount_in):
    decimals = {
    'ar': 12,
    'usdc': 6,
    'usdt':6,
    'eth':18,
    'ardrive':18,
    'acnh':8,
    'ans': 18,
    'u': 6,
    'stamp': 12,
    # 'map': 18,
    'aocred':3,
    'trunk':3,
    '0rbt':18,
    'halo':18,
    'exp(ario)':6
}

tags = {
    'ar': "arweave,ethereum-ar-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA,0x4fadc7a98f2dc96510e42dd1a74141eeae0c1543",
    'usdc': "ethereum-usdc-0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    'usdt': "ethereum-usdt-0xdac17f958d2ee523a2206206994597c13d831ec7",
    'eth': "ethereum-eth-0x0000000000000000000000000000000000000000",
    'ardrive':"arweave-ardrive--8A6RexFkpfWwuyVO98wzSFZh0d6VJuI-buTJvlwOJQ",
    'acnh': "everpay-acnh-0x72247989079da354c9f0a6886b965bcc86550f8a",
    'ans': "ethereum-ans-0x937efa4a5ff9d65785691b70a1136aaf8ada7e62",
    'u': 'arweave-u-KTzTXT_ANmF84fWEKHzWURD1LWd9QaFR9yfYUwH2Lxw',
    'stamp': 'arweave-stamp-TlqASNDLA1Uh8yFiH-BzR_1FDag4s735F3PoUFEv2Mo',
    # 'map': 'ethereum-map-0x9e976f211daea0d652912ab99b0dc21a7fd728e4',
    'aocred': 'aostest-aocred-Sa0iBLPNyJQrwpTTG-tWLQU-1QeUAJA73DdxGGiKoJc',
    'trunk': 'aostest-trunk-OT9qTE2467gcozb2g8R6D6N3nQS94ENcaAIJfUzHCww',
    '0rbt': 'aostest-0rbt-BUhZLMwQ6yZHguLtJYA5lLUa9LQzLXMXRfaq9FVcPJc',
    'halo':'psntest-halo-0x0000000000000000000000000000000000000000',
    'exp(ario)':'aostest-exp(ario)-aYrCboXVSl1AXL9gPFe3tfRxRf0ZmkOXH65mKT0HHZw'
}

    ps_router_url= urllib.parse.urljoin(ps_router_host, '/wsuser')
    token_in_tag = tags[token_in.lower()]
    token_out_tag = tags[token_out.lower()]
    token_in_decimals = decimals[token_in]
    token_out_decimals = decimals[token_out]

    query = {
        'event': 'query',
        'address': address,
        'tokenIn': token_in_tag,
        'tokenOut': token_out_tag,
        'amountIn': str(amount_in)
    }
    ws = create_connection(ps_router_url)
    ws.send(json.dumps(query))
    data = json.loads(ws.recv())
    if data['event'] == 'order':
        order = data
        order['tokenIn'] = token_in_tag
        order['tokenOut'] = token_out_tag
        order['amount_in'] = str(amount_in)
        order['amount_out'] = get_amount_out(address, order, token_out_tag)
        order['amount_in2'] = str(Decimal(int(order['amount_in']))/Decimal(10**token_in_decimals))
        order['amount_out2'] = str(Decimal(int(order['amount_out']))/Decimal(10**token_out_decimals))
        order['rate'] = float(order['amount_out2'])/float(order['amount_in2'])
        return order
    return data
