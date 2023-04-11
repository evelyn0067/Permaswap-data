import streamlit as st
from streamlit_extras.dataframe_explorer import dataframe_explorer
import pandas as pd
import requests

st.title("Orders data")
st.markdown(f'<h1 style="color:#33ff33;font-size:24px;">{"ColorMeBlue text”"}</h1>', unsafe_allow_html=True)
st.info('**you can query the swap order in there.**')
filtered_df = dataframe_explorer(st.session_state.order_datas)
st.dataframe(filtered_df, use_container_width=True)