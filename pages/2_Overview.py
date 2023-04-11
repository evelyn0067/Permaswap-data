import requests, datetime
from dateutil import parser
import streamlit as st
import pandas as pd
import altair as alt
import utils
st.title("Overview")

stats_host = 'https://stats.permaswap.network'
router_host = 'https://router.permaswap.network'
decimals = {
    'ar': 12,
    'usdc': 6,
    'usdt':6,
    'eth':18,
    'ardrive':12
}
pools = {
    'usdc-usdt': '0xdb7b3480f2d1f7bbe91ee3610664756b91bbe0744bc319db2f0b89efdf552064',
    'ar-usdc': '0x0750e26dbffb85e66891b71b9e1049c4be6d94dab938bbb06573ca6178615981',
    'ar-eth': '0x5f0ac5160cd3c105f9db2fb3e981907588d810040eb30d77364affd6f4435933',
    'eth-usdc': '0x7eb07d77601f28549ff623ad42a24b4ac3f0e73af0df3d76446fb299ec375dd5',
    'ar-ardrive': '0xdb7b3480f2d1f7bbe91ee3610664756b91bbe0744bc319db2f0b89efdf552064'
}

fee_ratios = {
    'usdc-usdt': 0.0005,
    'ar-usdc': 0.003,
    'ar-eth': 0.003,
    'eth-usdc': 0.003,
    'ar-ardrive':0.003
}

@st.cache_data(ttl=300)
def get_prices():
    prices = {
        'usdc': 1,
        'usdt':1,
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

respond = requests.get('https://router.permaswap.network/info').json()
pool_count = len(respond['poolList'])

cur = parser.parse(info['curStats']['date'])
if datetime.datetime.now(datetime.timezone.utc).date() == cur.date():
    today_volume = sum(info['curStats']['user'].values())
else:
    today_volume = 0

@st.cache_data
def get_stats():
    d1 = datetime.datetime(2022,12,12)
    d2 = datetime.datetime.today()
    interval = d2-d1
    stats = []
    day = datetime.date.today()
    for i in range(1, interval.days+1):
        day = day - datetime.timedelta(days=1)
        date = day.strftime('%Y-%m-%d')
        url = '%s/stats?date=%s'%(stats_host, date)
        data = requests.get(url).json()
        if str(data) == 'record not found':
            continue
        stats.append({
            'date': date,
            'stats':data
        })
        print(date)
    stats.reverse()
    return stats

stats = get_stats()
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

date = []
router_fees = []
tx_counts = []
user_counts = []
user_volumes = []
for s in stats:
    date.append(s['date'])
    router_fees.append(s['stats'].get('fee', 0))
    tx_counts.append(s['stats'].get('txCount', 0))
    user_counts.append(len(s['stats']['user']))
    user_volumes.append(sum(s['stats']['user'].values()))

df = pd.DataFrame({'date': date,
                   'router_fees': router_fees,
                   'user_counts': user_counts,
                   'user_volumes': user_volumes,
                   })

st.session_state.key = df

df['sum_user_volumes']=df['user_volumes'].cumsum()
df['sum_router_fee']=df['router_fees'].cumsum()

col1, col2 = st.columns(2)
col1.metric(':green[Total Trading Volume]', '%.2f $'%df.iloc[-1]['sum_user_volumes'])
col2.metric(":green[Total LP Fees]", '%.2f $'%df.iloc[-1]['sum_router_fee'])

col1, col2 = st.columns(2)
col1.metric(':green[Current Pool Count]', pool_count)
col2.metric(':green[Current LP Count]', lp_count)

col1, col2 = st.columns(2)
col1.metric(':green[Today (%s UTC) Volume]'%today.strftime('%Y-%m-%d'), '%.2f $'%today_volume)
col2.metric(":green[Current Total TVL]", '%.2f $'%total_tvl)

df1 = df[-30:]

# user volume
st.subheader('Daily Trading Volume')                  

base = alt.Chart(df1).encode(x='date')

bar = base.mark_bar(color='green').encode(
  y='user_volumes')

line =  base.mark_line(color='green').encode(
    y='user_counts'
)
st.altair_chart(bar)    

# user count
st.subheader('Daily User Amount')

c = alt.Chart(df1).mark_line(color='green').encode(
  x='date',
  y='user_counts')
st.altair_chart(c)    



