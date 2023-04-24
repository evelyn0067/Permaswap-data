import streamlit as st
import altair as alt
import pandas as pd
from streamlit_extras.dataframe_explorer import dataframe_explorer
import utils
with open("designing.css") as source_des:
    st.markdown(f"<style>{source_des.read()}</style>",unsafe_allow_html=True)
st.title("Users analysis")
data = utils.get_order_data()
df = data.resample('D').nunique()
df = df.astype(float)
df.reset_index(inplace=True)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date'] = df['timestamp'].dt.date
df = df.rename({'everHash': 'Swap Amount', 'Address': 'User Amount'}, axis=1)

base = alt.Chart(df).encode(x='date')


c = alt.Chart(df).mark_bar(color='green',size=13).encode(
  x='date',
  y='Swap Amount')

st.altair_chart(c,use_container_width=True)   


c = alt.Chart(df).mark_bar(color='green',size=15).encode(
  x='date',
  y='User Amount')

st.altair_chart(c,use_container_width=True)  
