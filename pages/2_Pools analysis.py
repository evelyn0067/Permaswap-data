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
from data import *
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

prices = get_prices2()
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

col1, col2 = st.columns(2)
col1.header('PooL')
pool = col2.selectbox(
    '',
    pools.keys())
st.header('Price')
col1, col2, col3 = st.columns(3)
token = col1.selectbox('', tokens_k)
period = col2.selectbox('', ['D', '8H', '4H', 'H'])

st.text("")

col1, col2 = st.columns(2)
col1.metric(':green[Current Price]', '%.3f usd/%s '%(prices[token], token))
col2.metric('', '%.4f %s/usd '%(1/prices[token], token))

orders = get_today_orders()
orders.extend(get_orders(yesterday, duration=30))
orders = process_orders(orders)
print(len(orders))

kline = get_kline(orders, token, period)

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
