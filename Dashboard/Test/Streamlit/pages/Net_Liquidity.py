# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 12:47:51 2023

@author: mydea
"""

import streamlit as st
import pandas as pd
import sqlalchemy
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
import yfinance as yf
import altair as alt
from datetime import datetime


from sqlalchemy import create_engine

#Databases
engine = create_engine('sqlite:///Database.db')

start = '1990-01-01'

ids = ['WALCL','WTREGEN', 'RRPONTSYD', 'SP500']

#DB Export
all_results = []
for id in ids:
    results = pd.read_sql(id, engine).set_index('index')
    all_results.append(results)
df = pd.concat(all_results, axis=1)
df = df.fillna(method='bfill')
df = df.fillna(method='ffill')
df = df.dropna()
df.columns = ids
df['NET_LIQ'] = (df.WALCL - df.WTREGEN * 1000 - df.RRPONTSYD * 1000)/(1000*1000)
df['SP_FV'] = df.SP500 - ((df.WALCL - df.WTREGEN * 1000 - df.RRPONTSYD * 1000)/1000/1.1-1625)


#Streamlit code
st.title('Indikatoren')

st.header('Net Liquidity und Vola - '  + str(df.index[-1].date()))

st.subheader('NL Fair Value S&P 500')
st.caption('If over 320 strong bearish sign, if under -100 bullish sign.')
st.line_chart(df.SP_FV.tail(250))

st.subheader('Net Liquidity')
st.line_chart(df.NET_LIQ.tail(250))

st.subheader('WALCL')
st.line_chart(df.WALCL.tail(250))

st.subheader('WTREGEN')
st.line_chart(df.WTREGEN.tail(250))

st.subheader('RRPONTSYD')
st.line_chart(df.RRPONTSYD.tail(250))

st.subheader('FV (rot) vs. SP500 (blau)')
fig, ax1 = plt.subplots()
ax1.plot(df.SP500.tail(250))
ax2 = ax1.twinx()
ax2.plot(df.SP_FV.tail(250), color='red', label="FV")
st.pyplot(fig)

