import streamlit as st
import plotly.graph_objs as go
import plotly.offline as py
import requests
import pandas as pd
from dateutil import parser
import altair as alt
import utils
import datetime
from plotly.subplots import make_subplots
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

data = utils.get_order_data()

col1, col2, col3 = st.columns(3)
col1.header('Price K-line')
token = col2.selectbox(
    '',
    ['AR','ETH','ARDRIVE','ACNH','ANS'])
period = col3.selectbox('', ['D', '8H', '4H', 'H'])
token = token.lower()
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
orders = utils.get_today_orders()
orders.extend(utils.get_orders(yesterday, duration=30))
orders = utils.process_orders(orders)
print(len(orders))

kline = utils.get_kline_new(orders, token, period)

print('kline:', kline.head())
trace = go.Candlestick(x=kline.index,
                       open=kline['price']['first'],
                       high=kline['price']['max'],
                       low=kline['price']['min'],
                       close=kline['price']['last'])

fig = make_subplots(rows=2,
    cols=1,
    row_heights=[0.8, 0.2],
    shared_xaxes=True,
    vertical_spacing=0.02)

fig.add_trace(trace, row=1, col=1)
fig.add_trace(go.Bar(x=kline.index, y=kline['volume']['sum'], marker=dict(color='green')),
               row=2,
               col=1)

fig.update_layout(title = token.upper()+'/USD Klines',
    yaxis1_title = 'Price (usd)',
    yaxis2_title = 'Volume (usd)',
    xaxis2_title = 'Time',
    xaxis1_rangeslider_visible = False,
    xaxis2_rangeslider_visible = False,
    yaxis2_showgrid = False,
    showlegend=False
)
st.plotly_chart(fig)



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

