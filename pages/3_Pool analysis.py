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
    frame = frame.replace('ethereum-ans-0x937efa4a5ff9d65785691b70a1136aaf8ada7e62', 'ANS')
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
    ['AR','ETH','ARDRIVE','ACNH','ANS'])

if token == 'ARDRIVE' or 'ACNH' or 'ANS':
    kline = utils.get_multikline(symbol=token,dataframe=data)

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
decimals = utils.decimals
pools = utils.pools
fee_ratios = utils.fee_ratios
prices = utils.get_prices()

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
col1.header('Pool')
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


df = pd.DataFrame({'date': date,
                   'volumes': vs,
                   'fees': fees})
df['date'] = df['date'].str.split('T').str[0]

df1 = df[:30]
col1, col2, col3 = st.columns(3)
col1.metric(':green[Token X]', '%.0f %s'%(tvl[pool][x], x.upper()))
col2.metric(':green[Token Y]', '%.0f %s'%(tvl[pool][y], y.upper()))
col3.metric(":green[LP count]", tvl[pool]['lp_count'])
st.subheader('Volume')

c = alt.Chart(df1).mark_bar(color='green').encode(
  x='date',
  y='volumes')

st.altair_chart(c,use_container_width=True)    

st.subheader('Fees')

c = alt.Chart(df1).mark_bar(color='green').encode(
  x='date',
  y='fees')

st.altair_chart(c,use_container_width=True)    

