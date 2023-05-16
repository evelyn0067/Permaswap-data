import streamlit as st
import plotly.graph_objs as go
import plotly.offline as py
import requests
import pandas as pd
from dateutil import parser
import altair as alt
import utils
import datetime
st.markdown("""
<style>
.css-h5rgaw.egzxvld1
{
    visibility: hidden;
}
.ag-row-odd ag-row-no-focus ag-row ag-row-level-0 ag-row-position-absolute
{
    visibility: hidden;
}
.ag-cell-wrapper
{
    visibility: hidden;
}
.gridToolBar
{
    visibility: hidden;
}
""",unsafe_allow_html=True)

with open("designing.css") as source_des:
    st.markdown(f"<style>{source_des.read()}</style>",unsafe_allow_html=True)
st.title("Pool analysis")

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
    frame = combined_df.loc[:,['Address','everHash','In Token','Out Token','In Token Amount','Out Token Amount','Price']]
    frame = frame.replace('arweave,ethereum-ar-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA,0x4fadc7a98f2dc96510e42dd1a74141eeae0c1543', 'AR')
    frame = frame.replace('arweave-ardrive--8A6RexFkpfWwuyVO98wzSFZh0d6VJuI-buTJvlwOJQ', 'ARDRIVE')
    frame = frame.replace('ethereum-eth-0x0000000000000000000000000000000000000000', 'ETH')
    frame = frame.replace('ethereum-usdc-0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', 'USDC')
    frame = frame.replace('ethereum-usdt-0xdac17f958d2ee523a2206206994597c13d831ec7', 'USDT')
    frame = frame.replace('everpay-acnh-0x72247989079da354c9f0a6886b965bcc86550f8a', 'ACNH')
    frame['Price'] = frame['Price'].astype(float)
    return frame


def get_kline(symbol,dataframe):
    df1 = dataframe[(dataframe['In Token']==symbol)&((dataframe['Out Token']=='USDT')|(dataframe['Out Token']=='USDC'))]
    df1['Price'] = 1/df1['Price']
    df2 = dataframe[(dataframe['Out Token']==symbol)&((dataframe['In Token']=='USDT')|(dataframe['In Token']=='USDC'))]
    df3 = pd.concat([df1,df2])
    df4 = df3.resample('D').agg({'Price': ['first', 'max', 'min', 'last']})
    return df4

data = get_order_data()

col1, col2 = st.columns(2)
col1.header('Price K-line')
token = col2.selectbox(
    '',
    ['AR','ETH','ARDRIVE'])

if token == 'ARDRIVE':
    kline1 = get_kline(symbol='ARDRIVE',dataframe=data)
    df1 = data[(data['In Token']=='ARDRIVE')&(data['Out Token']=='AR')]
    df1['Price'] = 1/df1['Price']
    df2 = data[(data['Out Token']=='ARDRIVE')&(data['In Token']=='AR')]
    kline1 = pd.concat([df1,df2])
    kline1 = kline1.sort_index()
    kline1['category']=1
    df3 = data[(data['In Token']=='AR')&((data['Out Token']=='USDT')|(data['Out Token']=='USDC'))]
    df3['Price'] = 1/df3['Price']
    df4 = data[(data['Out Token']=='AR')&((data['In Token']=='USDT')|(data['In Token']=='USDC'))]
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
            for b in range(0,x+1):
                print(x,b)
                if df_combain.iloc[x+b+1]['category']==2:
                    dataar = df_combain.iloc[x+b+1]
                    print(dataar,df_combain.iloc[x+b+1])
                    order.append(dataar)
                    print(dataar)
                    break
            hash.append(dataardrive['everHash'])
            price.append(dataardrive['Price']*dataar['Price'])
            price_dict[dataardrive['everHash']]= dataardrive['Price']*dataar['Price']
    kline1['Price'] = price
    df1 = data[(data['In Token']=='ARDRIVE')&((data['Out Token']=='USDT')|(data['Out Token']=='USDC'))]
    df1['Price'] = 1/df1['Price']
    df2 = data[(data['Out Token']=='ARDRIVE')&((data['In Token']=='USDT')|(data['In Token']=='USDC'))]
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

else:
    kline = get_kline(symbol=token,dataframe=data)

print(kline)

trace = go.Candlestick(x=kline.index,
                       open=kline['Price']['first'],
                       high=kline['Price']['max'],
                       low=kline['Price']['min'],
                       close=kline['Price']['last'])


layout = go.Layout(title=token+'/USD Klines',
                   xaxis=dict(title='Date'),
                   yaxis=dict(title='Price'))


fig = go.Figure(data=[trace], layout=layout)

st.plotly_chart(fig, use_container_width=True)


stats_host = 'https://stats.permaswap.network'
router_host = 'https://router.permaswap.network'
decimals = {
    'ar': 12,
    'usdc': 6,
    'usdt':6,
    'eth':18,
    'ardrive':18,
    'acnh':8,
    'ans': 18
}
pools = {
    'usdc-usdt': '0xdb7b3480f2d1f7bbe91ee3610664756b91bbe0744bc319db2f0b89efdf552064',
    'ar-usdc': '0x0750e26dbffb85e66891b71b9e1049c4be6d94dab938bbb06573ca6178615981',
    'ar-eth': '0x5f0ac5160cd3c105f9db2fb3e981907588d810040eb30d77364affd6f4435933',
    'eth-usdc': '0x7eb07d77601f28549ff623ad42a24b4ac3f0e73af0df3d76446fb299ec375dd5',
    'ar-ardrive': '0xbb546a762e7d5f24549cfd97dfa394404790293277658e42732ab3b2c4345fa3',
    'usdc-acnh': '0x7200199c193c97012893fd103c56307e44434322439ece7711f28a8c3512c082',
    'ar-ans': '0x6e80137a5bbb6ae6b683fcd8a20978d6b4632dddc78aa61945adbcc5a197ca0f'

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
    'ar-ans': 0.003
}

@st.cache_data(ttl=300)
def get_prices():
    prices = {
        'usdc': 1,
        'usdt':1,
        'acnh':0.147,
        'ans':2.0
    }
    prices['ar'] = utils.get_price_from_redstone('ar', 'usdc')
    prices['eth'] = utils.get_price_from_redstone('eth', 'usdc')
    prices['ardrive'] = utils.get_price_from_redstone('ardrive','usdc')
    return prices
prices = get_prices()
print('prices', prices)

@st.cache_data(ttl=300)
def get_info():
    url = '%s/info'%stats_host
    return requests.get(url).json()
info = get_info()
#pool_count = len(info['pool'])
pool_count = 4

cur = parser.parse(info['curStats']['date'])
if datetime.datetime.now(datetime.timezone.utc).date() == cur.date():
    today_volume = sum(info['curStats']['user'].values())
else:
    today_volume = 0

stats = utils.get_stats()
today = datetime.date.today()

@st.cache_data(ttl=300)
def get_lps():
    lps = {}
    for k, v in pools.items():
        url = '%s/lps?poolid=%s'%(router_host, v)
        data = requests.get(url).json()
        lps[k] = data['lps']
    return lps
lps = get_lps()
lp_count = sum([len(v) for k, v in lps.items()])
print('lps:', lps)

# tvl
tvl = {}
total_tvl = 0
for pair, lps in lps.items():
    x, y = pair.split('-')
    tvl[pair] = {}
    tvl[pair]['lp_count'] = len(lps)
    dx = decimals[x]
    dy = decimals[y]
    for lp in lps:
        ax, ay = utils.liquidity_to_amount2(lp['liquidity'], lp['lowSqrtPrice'], lp['highSqrtPrice'], lp['currentSqrtPrice'])
        ax, ay = int(ax)/10**dx, int(ay)/10**dy
        print(ax, ay)
        tvl[pair][x] = tvl[pair].get(x, 0) + ax
        tvl[pair][y] = tvl[pair].get(y, 0) + ay
        total_tvl += prices[x] * ax 
        total_tvl += prices[y] * ay
print('total_tvl:', total_tvl)
print('tvl:', tvl)

col1, col2 = st.columns(2)
col1.header('PooL')
pool = col2.selectbox(
    '',
    pools.keys())

# tvl
st.subheader('Current Pool %s TVL'%pool.upper())
#st.text('Lp count: %i'%tvl[pool]['lp_count'])
x, y = pool.split('-')
#st.text('%s: %s'%(x, tvl[pool][x]))
#st.text('%s: %s'%(y, tvl[pool][y]))

date = []
vs = []
fees = []
for s in stats:
    date.append(s['date'])
    v = s['pool'].get(pools[pool], 0)
    vs.append(v)
    fee_ratio = fee_ratios[pool]
    fees.append(v*fee_ratio)

st.subheader('Volume')

df = pd.DataFrame({'date': date,
                   'volumes': vs,
                   'fees': fees})
df['date'] = df['date'].str.split('T').str[0]

df1 = df[:30]
col1, col2, col3 = st.columns(3)
col1.metric(':green[Token X]', '%.0f %s'%(tvl[pool][x], x.upper()))
col2.metric(':green[Token Y]', '%.0f %s'%(tvl[pool][y], y.upper()))
col3.metric(":green[LP count]", tvl[pool]['lp_count'])

c = alt.Chart(df1).mark_bar(color='green').encode(
  x='date',
  y='volumes')

st.altair_chart(c,use_container_width=True)    

st.subheader('Fees')

c = alt.Chart(df1).mark_bar(color='green').encode(
  x='date',
  y='fees')

st.altair_chart(c,use_container_width=True)    

