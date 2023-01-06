# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 12:35:37 2023

@author: mydea
"""

import matplotlib.pyplot as plt
import pandas as pd
import quandl as ql
import streamlit as st
authtoken=''

#%matplotlib inline

yield_ = ql.get("USTREASURY/YIELD", authtoken=authtoken)
today = yield_.iloc[-1,:]
month_ago = yield_.iloc[-30,:]
df = pd.concat([today, month_ago], axis=1)
df.columns = ['today', 'month_ago']

#df.plot(style={'today': 'ro-', 'month_ago': 'bx--'}
 #       ,title='Treasury Yield Curve, %');

st.subheader('Treasury Yield Curve')
st.line_chart(df)



