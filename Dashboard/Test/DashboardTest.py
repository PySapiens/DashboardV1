import streamlit as st
import pandas as pd
import sqlalchemy
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
from fredapi import Fred
fred_key = '9a9c69745bc32b9678c0207caa1a119a'
#import ta
import yfinance as yf

#create fred object
fred = Fred(api_key=fred_key)

ids = ('WALCL','WTREGEN', 'RRPONTSYD', 'SP500', 'TOTALSA', 'RSXFS')

all_results = []

for myid in ids:
    results = fred.get_series(series_id=myid)
    results = results.to_frame(name=myid)
    all_results.append(results)
    
df = pd.concat(all_results, axis=1)
#df = df.dropna()
df = df.fillna(method='bfill')
df = df.fillna(method='ffill')
df = df.dropna()

df['NET_LIQ'] = (df.WALCL - df.WTREGEN * 1000 - df.RRPONTSYD * 1000)/(1000*1000)
df['SP_FV'] = df.SP500 - ((df.WALCL - df.WTREGEN * 1000 - df.RRPONTSYD * 1000)/1000/1.1-1625)

sp_fv = df['SP_FV'].tail(250).plot()
#sp_fv.axhline(y = 350, color = 'r', linestyle = '-')
#plt.show()

nl_df = df['NET_LIQ'].tail(250)

fv_df = df['SP_FV'].tail(250)
#fv_df['up_signal'] = df['SP_FV'] * 0 + 350

#streamlit code
st.title('Indikatoren')

st.header('Net Liquidity und Vola')

st.subheader('Net Liquidity')
st.line_chart(nl_df)

st.subheader('NL Fair Value S&P 500')
st.line_chart(fv_df)

st.subheader('Test')
fig, ax1 = plt.subplots()
ax1.plot(df.SP500)
ax2 = ax1.twinx()
ax2.plot(df.SP_FV, color='red', label="FV")
st.pyplot(fig)

