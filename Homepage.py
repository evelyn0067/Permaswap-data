import streamlit as st
import base64
import streamlit.components.v1 as com
from PIL import Image

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

image = Image.open('Group 37818.png')

col1,col2 = st.columns([1,7])
with col1:
    #com.iframe('https://embed.lottiefiles.com/animation/138008')
    st.image(image)
with col2:
    st.header('PermaswapDashboard')
# st.image("https://arseed.web3infra.dev/nryZxpbQFXhlLvVdZi-GSjs2yQPoH-YaVaUVlkM9vr4")
st.subheader('Summary')
# file_ = open("/Users/evelyn/Desktop/Permaswapdata_app/gifgit (1).gif", "rb")
# contents = file_.read()
#data_url = base64.b64encode(contents).decode("utf-8")
# file_.close()

# st.markdown(
#    f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
#    unsafe_allow_html=True,
#)
#file_ = open("/Users/evelyn/Desktop/Permaswapdata_app/gifgit (1).gif", "rb")
#contents = file_.read()
#data_url = base64.b64encode(contents).decode("utf-8")
#file_.close()

#st.markdown(
#    f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
#    unsafe_allow_html=True,
#)

#col1, col2 = st.columns([1, 5])

#col1.markdown(
#    "![Alt Text](https://s6.aconvert.com/convert/p3r68-cdx67/tt7ef-by9gt.gif)"
#)

#col2.header('DASHBOARD') 

st.markdown("""
    <style>
    a[href] {
        text-decoration: none;
        color: #61AA69;
    }
""", unsafe_allow_html=True)
st.write(
    """
    Welcome to the Permaswap dashboard which is geared to monitoring and analyzing various metrics related to Permaswap. 
    It allows users to track difference token performances, trading pairs, identifying trends as well as patterns 
    and of course to make informed decisions.
    
    Just a reminder that Permaswap is a cross-chain DEX network with 0 gas fees and having all transactions delivered INSTANTLY. 
    All swaps that are done instantly are powered by everPay! Our goal? Allow you to easily swap different assets from different chains 
    in one place for a quick and easy experience.
    """
)
st.markdown(
    '''
       * Website: [Permaswap.network](https://permaswap.network/#/)
       * Twitter: [@Permaswap](https://twitter.com/Permaswap)
       * WhitePaper: [Permaswap WhitePaper](https://mirror.xyz/permaswap.eth/ustZcDgavlm4xmYI26thEAj8W2cXlZpRkG5Jqz0iS14) 
       * Governance DAO: [PSCP](https://permadao.notion.site/Permaswap-69ba28d2d17643ae9711947329138c58)
    '''
)
st.subheader('Usage')
st.markdown(
    '''
       * Overview: You can get the overall data of Permaswap
       * Pool Analysis: This part contain specific data of the pool 
       * Users Analysis: This is about the users of Permaswap 
       * Order Data: You can query all the transactions in Permaswap within 30 days
    '''
)
st.subheader('Future Works')
st.write(
    """
    This tool is a work in progress and will continue to be developed moving forward. Adding other metrics, 
    optimizing the code in general, enhancing the UI/UX of the tool, and more importantly,
    improving the data pipeline by utilizing are among the top priorities for the development of this app. Feel free 
    to share your feedback, suggestions, and also critics in our discord.
    """
)

c1, c2, c3 = st.columns(3)
with c1:
    st.info('**Join our community: [Discord](https://discord.gg/G5UDdPbbkP)**', icon="🔖")
with c2:
    st.info('**More API information: [Development docs](https://permadao.notion.site/Permaswap-WIKI-EN-485cd6623f954902b61775e4f1a86717)**', icon="💻")
with c3:
    st.info('**Supported by everVison: [everVision](https://ever.vision/#/)**', icon="💪🏻")
