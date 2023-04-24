import streamlit as st
import base64
st.image("https://arseed.web3infra.dev/nryZxpbQFXhlLvVdZi-GSjs2yQPoH-YaVaUVlkM9vr4")
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


st.write(
    """
    This is the dashboard of Permaswap which is amied to monitor and analyze various metrics 
    related to Permaswap. It allows users to track the performance of different tokens and trading 
    pairs, identify trends and patterns, and make informed decisions.

    Permaswap is a cross-chain DEX network with 0 gas fees, provided by @everVisionHQ. 
    All swaps are done INSTANTLY with the power of the everPay protocol. Our goal? 
    Allow you to easily swap different assets from different chains in one place for a quick and efficient experience.
    
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
       * Pool Analysis: This part cantain specific data of the pool 
       * Users Analysis: This about the users of Permaswap 
       * Order Data: You can query recent order
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