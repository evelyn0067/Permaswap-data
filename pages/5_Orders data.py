import streamlit as st
from streamlit_extras.dataframe_explorer import dataframe_explorer
import pandas as pd
import requests
import datetime
import utils
with open("designing.css") as source_des:
    st.markdown(f"<style>{source_des.read()}</style>",unsafe_allow_html=True)
st.title("Orders data")
data = utils.get_order_data()
df = data.reindex(columns=['Address','In Token','Out Token','In Token Amount','Out Token Amount','Price','everHash'])
st.info('**you can query the swap order in there.**')
filtered_df = dataframe_explorer(df)
st.dataframe(filtered_df, use_container_width=True)
