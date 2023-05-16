from decimal import Decimal
import requests
from urllib.parse import urlencode, quote_plus
import pandas as pd
import datetime
import streamlit as st

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
@st.cache_data(ttl=300)
def get_order_data():
    day_end = datetime.date.today()
    date_end = day_end.strftime('%Y-%m-%d')
    day_start = day_end - datetime.timedelta(days=30)
    date_start= day_start.strftime('%Y-%m-%d')
    combined_df = pd.DataFrame()
    url = 'https://router.permaswap.network/orders/?start='+date_start+'&end='+date_end+'&count=50&page='
    for x in range(0,5000000):
        page = x+1
        print(page)
        page = str(page)
        url1 = url+page
        print(url)
        response = requests.get(url1)
        data = response.json()
        df = pd.DataFrame(data['orders'])
        combined_df = pd.concat([combined_df,df])
        if len(df) < 50:
            break
    combined_df.set_index('timestamp', inplace=True)
    combined_df.index = pd.to_datetime(combined_df.index, unit='ms')
    combined_df.sort_values("id")
    combined_df = combined_df.rename({'timestap': 'Time', 'address': 'Address','tokenInTag':'In Token','tokenOutTag':'Out Token','tokenInAmount':'In Token Amount','tokenOutAmount':'Out Token Amount','price':'Price'}, axis=1)
    frame = combined_df.loc[:,['Address','In Token','Out Token','In Token Amount','Out Token Amount','Price','everHash']]
    frame = frame.replace('arweave,ethereum-ar-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA,0x4fadc7a98f2dc96510e42dd1a74141eeae0c1543', 'AR')
    frame = frame.replace('arweave-ardrive--8A6RexFkpfWwuyVO98wzSFZh0d6VJuI-buTJvlwOJQ', 'ARDRIVE')
    frame = frame.replace('ethereum-eth-0x0000000000000000000000000000000000000000', 'ETH')
    frame = frame.replace('ethereum-usdc-0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', 'USDC')
    frame = frame.replace('ethereum-usdt-0xdac17f958d2ee523a2206206994597c13d831ec7', 'USDT')
    frame = frame.replace('everpay-acnh-0x72247989079da354c9f0a6886b965bcc86550f8a', 'ACNH')
    frame = frame.replace('ethereum-ans-0x937efa4a5ff9d65785691b70a1136aaf8ada7e62', 'ANS')
    frame['Price'] = frame['Price'].astype(float)
    return frame

@st.cache_data
def get_stats():
    day_end = datetime.date.today()
    date_end = day_end.strftime('%Y-%m-%d')
    day_start = day_end - datetime.timedelta(days=30)
    date_start= day_start.strftime('%Y-%m-%d')
    url = 'https://stats.permaswap.network/stats?start='+date_start+'&end='+date_end+'&count=50&page=1'
    response = requests.get(url)
    data= response.json()
    for i in range(0,10000):
        day_end = day_start - datetime.timedelta(days=1)
        date_end = day_end.strftime('%Y-%m-%d')
        day_start = day_end - datetime.timedelta(days=30)
        date_start= day_start.strftime('%Y-%m-%d')
        url = 'https://stats.permaswap.network/stats?start='+date_start+'&end='+date_end+'&count=50&page=1'
        print(url)
        response = requests.get(url)
        data_recive = response.json()
        data = data + data_recive
        if len(data_recive) < 30:
            break
    return data
