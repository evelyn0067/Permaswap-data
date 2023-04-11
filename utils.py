from decimal import Decimal
import requests
from urllib.parse import urlencode, quote_plus

HALF = Decimal('0.5')

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
    #print(url)
    result = requests.get(url).json()
    price = result[token.upper()]['value']/result[currency.upper()]['value']
    return price