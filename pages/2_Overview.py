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
decimals = {
    'ar': 12,
    'usdc': 6,
    'usdt':6,
    'eth':18,
    'ardrive':18,
    'acnh':8,
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
        'acnh':0.147
        'ans': 2.0
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



