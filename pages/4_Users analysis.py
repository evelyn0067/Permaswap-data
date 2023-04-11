import streamlit as st
import altair as alt
from streamlit_extras.dataframe_explorer import dataframe_explorer
st.title("Users analysis")
data = st.session_state.order_datas
df = data.resample('D').nunique()
df = df.astype(float)
df.reset_index(inplace=True)

base = alt.Chart(df).encode(x='date')

filtered_df = dataframe_explorer(df)
st.dataframe(filtered_df, use_container_width=True)

c = alt.Chart(df).mark_bar(color='green',size=13).encode(
  x='timestamp',
  y='everHash')

st.altair_chart(c,use_container_width=True)   


c = alt.Chart(df).mark_bar(color='green',size=15).encode(
  x='timestamp',
  y='Address')

st.altair_chart(c,use_container_width=True)  
