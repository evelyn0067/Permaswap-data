import requests, datetime
from dateutil import parser
import streamlit as st
import pandas as pd
import altair as alt
import utils
from PIL import Image
from st_aggrid import AgGrid

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
st.title("Overview")
stats_host = 'https://stats.permaswap.network'
router_host = 'https://router.permaswap.network'
decimals = utils.decimals
pools = utils.pools
fee_ratios = utils.fee_ratios
prices = utils.get_prices()
print('prices', prices)
print(pools)

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
    tvl[pair]['LP Amount'] = len(lps)
    dx = decimals[x]
    dy = decimals[y]
    for lp in lps:
        ax, ay = utils.liquidity_to_amount2(lp['liquidity'], lp['lowSqrtPrice'], lp['highSqrtPrice'], lp['currentSqrtPrice'])
        ax, ay = int(ax)/10**dx, int(ay)/10**dy
        tvl[pair][x] = tvl[pair].get(x, 0) + ax
        tvl[pair][y] = tvl[pair].get(y, 0) + ay
        total_tvl += prices[x] * ax 
        total_tvl += prices[y] * ay
        tvl[pair]['TVL'] = prices[x] * tvl[pair][x] + prices[y] * tvl[pair][y]
print('total_tvl:', total_tvl)
print('tvl:', tvl)

date = []
router_fees = []
tx_counts = []
user_counts = []
user_volumes = []
for s in stats:
    date.append(s['date'])
    router_fees.append(s['fee'])
    tx_counts.append(s['txCount'])
    user_counts.append(len(s['user']))
    user_volumes.append(sum(s['user'].values()))

df = pd.DataFrame({'date': date,
                   'router_fees': router_fees,
                   'user_counts': user_counts,
                   'user_volumes': user_volumes,
                   })


df['sum_user_volumes']=df['user_volumes'].cumsum()
df['sum_router_fee']=df['router_fees'].cumsum()

col1, col2, col3 = st.columns(3)
col1.metric(':green[Total Trading Volume]', '{:,.0f} $'.format(df.iloc[-1]['sum_user_volumes']))
col2.metric(":green[Total LP Fees]", '{:,.0f} $'.format(df.iloc[-1]['sum_router_fee']))
col3.metric(":green[Current Total TVL]", '{:,.0f} $'.format(total_tvl))

#col1, col2 = st.columns(2)
#col1.metric(':green[Current Pool Count]', pool_count)
#col2.metric(':green[Current LP Count]', lp_count)

#col1, col2 = st.columns(2)
#col1.metric(':green[Today (%s UTC) Volume]'%today.strftime('%Y-%m-%d'), '%.2f $'%today_volume)
#col2.metric(":green[Current Total TVL]", '%.2f $'%total_tvl)
st.empty()
st.subheader('Support Token')

c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12 = st.columns([1,1.1,1,1.1,1,1.3,1,1.1,1,1.1,1,1.1])

c1.image(Image.open('ar.png'))
c2.text('AR')

c3.image(Image.open('acnh.png'))
c4.text('ACNH')

c5.image(Image.open('ardrive.png'))
c6.text('ARDRIVE')

c7.image(Image.open('usdc.png'))
c8.text('USDC')

c9.image(Image.open('usdt.png'))
c10.text('USDT')

c11.image(Image.open('eth.png'))
c12.text('ETH')

pd_tvl = pd.DataFrame(tvl)
df_pool = pd_tvl.transpose()
df_pool['Ratio'] = df_pool['TVL']/df_pool['TVL'].sum()
df_pool['Ratio'] = df_pool['Ratio'].apply(lambda x: format(x,'.2%')) 
df_pool[['LP Amount','TVL']] = df_pool[['LP Amount','TVL']].astype('int64')
df_pool = df_pool.loc[:,['LP Amount','TVL','Ratio']]
df_pool = df_pool.sort_values('TVL',ascending=False)
df_pool = df_pool.reset_index()
df_pool.style.set_properties(**{"background-color": "black", "color": "lawngreen"})
AgGrid(df_pool)
df1 = df[:30]
df1['date'] = df1['date'].str.split('T').str[0]


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



