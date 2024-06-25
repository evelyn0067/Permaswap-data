from decimal import Decimal
import requests
from urllib.parse import urlencode, quote_plus
import pandas as pd
import datetime
import streamlit as st

stats_host = 'https://stats.permaswap.network'
router_host = 'https://router.permaswap.network'

decimals = {
    'ar': 12,
    'usdc': 6,
    'usdt':6,
    'eth':18,
    'ardrive':18,
    'acnh':8,
    'ans': 18,
    'u':6,
    'stamp': 12
}

pools = {
    'usdc-usdt': '0xdb7b3480f2d1f7bbe91ee3610664756b91bbe0744bc319db2f0b89efdf552064',
    'ar-usdc': '0x0750e26dbffb85e66891b71b9e1049c4be6d94dab938bbb06573ca6178615981',
    'ar-eth': '0x5f0ac5160cd3c105f9db2fb3e981907588d810040eb30d77364affd6f4435933',
    'eth-usdc': '0x7eb07d77601f28549ff623ad42a24b4ac3f0e73af0df3d76446fb299ec375dd5',
    'ar-ardrive': '0xbb546a762e7d5f24549cfd97dfa394404790293277658e42732ab3b2c4345fa3',
    'usdc-acnh': '0x7200199c193c97012893fd103c56307e44434322439ece7711f28a8c3512c082',
    'ar-ans': '0x6e80137a5bbb6ae6b683fcd8a20978d6b4632dddc78aa61945adbcc5a197ca0f',
    'ar-u': '0xdc13faadbd1efdaeb764f5515b20d88c5b9fa0c507c0717c7013b1725e398717',
    'ar-stamp': '0x94170544e7e25b6fc216eb044c1c283c89781bfb92bfeda3054488497bd654b6'
}

fee_ratios = {
    'usdc-usdt': 0.0005,
    'ar-usdc': 0.003,
    'ar-eth': 0.003,
    'eth-usdc': 0.003,
    'ar-usdt': 0.003,
    'eth-usdt': 0.003,
    'ar-ardrive': 0.003,
    'usdc-acnh':0.0005,
    'ar-ans': 0.003,
    'ar-u': 0.003,
    'ar-stamp': 0.003
}

symbol_to_tag = {
    'ar': 'arweave,ethereum-ar-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA,0x4fadc7a98f2dc96510e42dd1a74141eeae0c1543',
    'usdc': 'ethereum-usdc-0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
    'usdt': 'ethereum-usdt-0xdac17f958d2ee523a2206206994597c13d831ec7',
    'eth': 'ethereum-eth-0x0000000000000000000000000000000000000000',
    'ardrive': 'arweave-ardrive--8A6RexFkpfWwuyVO98wzSFZh0d6VJuI-buTJvlwOJQ',
    'acnh': 'everpay-acnh-0x72247989079da354c9f0a6886b965bcc86550f8a',
    'ans': 'ethereum-ans-0x937efa4a5ff9d65785691b70a1136aaf8ada7e62',
    'u': 'arweave-u-KTzTXT_ANmF84fWEKHzWURD1LWd9QaFR9yfYUwH2Lxw',
    'stamp': 'arweave-stamp-TlqASNDLA1Uh8yFiH-BzR_1FDag4s735F3PoUFEv2Mo'
}

tag_to_symbol = {value: key for key, value in symbol_to_tag.items()}


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
    result = requests.get(url).json()
    price = result[token.upper()]['value']/result[currency.upper()]['value']
    return price

@st.cache_data(ttl=300)
def get_prices():
    prices = {
        'usdc': 1,
        'usdt':1,
        'acnh':0.147,
        'ans':2.0,
        'u':0.8,
        'stamp': 0.06
    }
    prices['ar'] = get_price_from_redstone('ar', 'usdc')
    prices['eth'] = get_price_from_redstone('eth', 'usdc')
    prices['ardrive'] = get_price_from_redstone('ardrive','usdc')
    return prices
prices = get_prices()
print('prices', prices)

@st.cache_data(ttl=300)
def get_order_data():
    day_end = datetime.date.today()
    date_end = day_end.strftime('%Y-%m-%d')
    day_start = day_end - datetime.timedelta(days=30)
    date_start= day_start.strftime('%Y-%m-%d')
    combined_df = pd.DataFrame()
    url = 'https://router.permaswap.network/orders/?start='+date_start+'&end='+date_end+'&count=200&page='
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
        if len(df) < 200:
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
    frame = frame.replace('arweave-u-KTzTXT_ANmF84fWEKHzWURD1LWd9QaFR9yfYUwH2Lxw', 'U')
    frame = frame.replace('arweave-stamp-TlqASNDLA1Uh8yFiH-BzR_1FDag4s735F3PoUFEv2Mo', 'STAMP')
    frame = frame.replace('ethereum-map-0x9e976f211daea0d652912ab99b0dc21a7fd728e4', 'MAP')
    frame['Price'] = frame['Price'].astype(float)
    return frame


@st.cache_data(ttl=300)    
def get_orders(end, start='', duration=30):
    orders = []
    if start == '':
        start = end - datetime.timedelta(days=duration)
    for page in range(1, 50000):
        url = '%s/orders?start=%s&end=%s&count=200&page=%i'%(router_host, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'), page)
        print(url)
        data = requests.get(url).json()
        orders.extend(data['orders'])
        if len(data['orders']) < 200:
            break
    return orders

@st.cache_data(ttl=300)
def get_today_orders():
    start = datetime.datetime.today()
    return get_orders(start, start)

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


def get_kline(symbol,dataframe):
    df1 = dataframe[(dataframe['In Token']==symbol)&((dataframe['Out Token']=='USDT')|(dataframe['Out Token']=='USDC'))]
    df1['Price'] = 1/df1['Price']
    df2 = dataframe[(dataframe['Out Token']==symbol)&((dataframe['In Token']=='USDT')|(dataframe['In Token']=='USDC'))]
    df3 = pd.concat([df1,df2])
    df4 = df3.resample('D').agg({'Price': ['first', 'max', 'min', 'last']})
    return df4


def get_multikline(symbol,dataframe):
    kline1 = get_kline(symbol=symbol,dataframe=dataframe)
    df1 = dataframe[(dataframe['In Token']==symbol)&(dataframe['Out Token']=='AR')]
    df1['Price'] = 1/df1['Price']
    df2 = dataframe[(dataframe['Out Token']==symbol)&(dataframe['In Token']=='AR')]
    kline1 = pd.concat([df1,df2])
    kline1 = kline1.sort_index()
    kline1['category']=1
    df3 = dataframe[(dataframe['In Token']=='AR')&((dataframe['Out Token']=='USDT')|(dataframe['Out Token']=='USDC'))]
    df3['Price'] = 1/df3['Price']
    df4 = dataframe[(dataframe['Out Token']=='AR')&((dataframe['In Token']=='USDT')|(dataframe['In Token']=='USDC'))]
    kline2 = pd.concat([df3,df4])
    kline2['category']=2
    hash = []
    price = []
    order = []
    price_dict = {}
    df_combain = pd.concat([kline1,kline2])
    df_combain = df_combain.sort_index()
    for x in range(0,len(df_combain)):
        print(x)
        if df_combain.iloc[x]['category']==1:
            dataardrive = df_combain.iloc[x]
            order.append(dataardrive)
            for b in range(0,len(df_combain)):
                if x+b+1 < len(df_combain):
                    if df_combain.iloc[x+b+1]['category']==2:
                        dataar = df_combain.iloc[x+b+1]
                        print(dataar,df_combain.iloc[x+b+1])
                        order.append(dataar)
                        print(dataar)
                        break
                else:
                    if df_combain.iloc[x-b-1]['category']==2:
                        dataar = df_combain.iloc[x-b-1]
                        print(dataar,df_combain.iloc[x-b-1])
                        order.append(dataar)
                        print(dataar)
                        break
            hash.append(dataardrive['everHash'])
            price.append(dataardrive['Price']*dataar['Price'])
            price_dict[dataardrive['everHash']]= dataardrive['Price']*dataar['Price']
    kline1['Price'] = price
    df1 = dataframe[(dataframe['In Token']==symbol)&((dataframe['Out Token']=='USDT')|(dataframe['Out Token']=='USDC'))]
    df1['Price'] = 1/df1['Price']
    df2 = dataframe[(dataframe['Out Token']==symbol)&((dataframe['In Token']=='USDT')|(dataframe['In Token']=='USDC'))]
    df3 = pd.concat([df1,df2])
    kline = pd.concat([kline1,df3])
    kline = kline.sort_index()
    kline = kline.resample('D').agg({'Price': ['first', 'max', 'min', 'last']})  
    prev_b = kline['Price']['last'].shift(1)
    prev_a = kline['Price']['min'].shift(1)
    kline['Price']['last'].fillna(prev_b, inplace=True)
    kline['Price']['min'].fillna(prev_b, inplace=True)
    kline['Price']['max'].fillna(prev_b, inplace=True)
    kline['Price']['first'].fillna(prev_b, inplace=True)
    kline.fillna(method='ffill', inplace=True)
    return kline


def get_volume(order, order_ref):
    token_in = tag_to_symbol[order['tokenInTag']]
    token_out = tag_to_symbol[order['tokenOutTag']]
    amount_in = float(order['tokenInAmount'])
    amount_out = float(order['tokenOutAmount'])
    
    token_in_ref = tag_to_symbol[order_ref['tokenInTag']]
    token_out_ref = tag_to_symbol[order_ref['tokenOutTag']]
    amount_in_ref = float(order_ref['tokenInAmount'])
    amount_out_ref = float(order_ref['tokenOutAmount'])
    
    if token_in == token_in_ref and token_out_ref in ['usdc', 'usdt']:
        price_token_in = amount_out_ref/amount_in_ref
        volume = price_token_in * amount_in
        return volume
    
    if token_out == token_in_ref and token_out_ref in ['usdc', 'usdt']:
        price_token_out = amount_out_ref/amount_in_ref
        volume = price_token_out * amount_out
        return volume
           
                
    if token_in == token_out_ref and token_in_ref in ['usdc', 'usdt']:
        price_token_in = amount_in_ref/amount_out_ref
        volume = price_token_in * amount_in
        return volume
       
    if token_out == token_out_ref and token_in_ref in ['usdc', 'usdt']:
        price_token_out = amount_in_ref/amount_out_ref
        volume = price_token_out * amount_out
        return volume
    
    return -1
            
def process_orders(orders):
    new_orders = []
    n = len(orders)
    
    for index, order in enumerate(orders):
        token_in = tag_to_symbol[order['tokenInTag']]
        token_out = tag_to_symbol[order['tokenOutTag']]
        amount_in = float(order['tokenInAmount'])
        amount_out = float(order['tokenOutAmount'])
        volume = 0

        new_order = {
            'time': order['timestamp'],
            'address': order['address'],
            'ever_hash': order['everHash'],
            'token_in': token_in,
            'token_out': token_out,
            'amount_in': amount_in,
            'amount_out': amount_out,
        }
        
        if token_in in ['usdc', 'usdt']:
            volume = float(order["tokenInAmount"])
            new_order['volume'] = volume
            new_orders.append(new_order)
            continue

        if token_out in ['usdc', 'usdt']:
            volume = float(order["tokenOutAmount"])
            new_order['volume'] = volume
            new_orders.append(new_order)
            continue
            
        for i in range(100):
            if index + i < n - 1:
                order_next = orders[index + i]
                volume = get_volume(order, order_next)
                if volume > 0:
                    new_order['volume'] = volume
                    new_orders.append(new_order)
                    break
                
            if index - i > 0:
                order_prev = orders[index - i]
                volume = get_volume(order, order_prev)
                if volume > 0:
                    new_order['volume'] = volume
                    new_orders.append(new_order)
                    break
    
    return new_orders

def get_kline_new(orders, token, period):
    df = pd.DataFrame(orders)
    print(df.head())
    df.set_index('time', inplace=True)
    df.index = pd.to_datetime(df.index, unit='ms')
    df1 = df[(df['token_in'] == token)].copy()
    df1.loc[:, 'price'] = df1['volume'] / df1['amount_in']
    df2 = df[(df['token_out'] == token)].copy()
    df2.loc[:, 'price'] = df2['volume'] / df2['amount_out']

    df3 = pd.concat([df1,df2])
    df4 = df3.resample(rule=period).agg(
        {'price': ['first', 'max', 'min', 'last'],     
        'volume': 'sum'
    })
    prev = df4['price']['last'].shift(1)
    df4['price', 'last'] = df4['price']['last'].fillna(prev)
    df4['price', 'min'] = df4['price']['min'].fillna(prev)
    df4['price', 'max'] = df4['price']['max'].fillna(prev)
    df4['price', 'first'] = df4['price']['first'].fillna(prev)
    df4 = df4.fillna(method='ffill')
    return df4
