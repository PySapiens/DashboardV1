# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 13:10:41 2023

@author: mydea
"""
import yfinance as yf
import pandas as pd
import quandl
key='' #nasdaq auth
import streamlit as st
from sqlalchemy import create_engine

#Databases
engine = create_engine('sqlite:///Database.db')

ids = ['^VIX', '^VIX3M','^GSPC']

all_results = []
for id in ids:
    results = pd.read_sql(id, engine).set_index('Date')
    results = results['Adj Close']
    all_results.append(results)
df = pd.concat(all_results, axis=1)
df = df.fillna(method='bfill')
df = df.fillna(method='ffill')
df = df.dropna()
df.columns = ids

#indicators
df['VRATIO'] = df['^VIX3M']/df['^VIX'] #contango/bwd in cash contracts
#df['CTNGO'] = (quandl.get("CHRIS/CBOE_VX1", authtoken=key)['Close'])/(quandl.get("CHRIS/CBOE_VX2", authtoken=key)['Close'])
df['RVOLA'] = df['^GSPC'].pct_change().rolling(30).std()*(252**0.5)*100 #realized volatility
df['RVOLA5'] = df['^GSPC'].pct_change().rolling(5).std()*(252**0.5)*100 #realized volatility
df['RVOLA10'] = df['^GSPC'].pct_change().rolling(10).std()*(252**0.5)*100 #realized volatility
df['VRP'] = df['^VIX'] - df['RVOLA10'] #vola risk premium
df['VRP5'] = df['VRP'].rolling(10).mean() #vrp 5 day ma
df['FVRP'] = (df['^VIX'].ewm(span=7, adjust=False).mean()) - df['RVOLA5'] #fast vola risk premium
df['VIXEMA'] = df['^VIX'].ewm(span=7, adjust=False).mean()


#STREAMLIT

st.subheader('VRATIO')
st.line_chart(df['VRATIO'].tail(250))

st.subheader('VRP')
st.line_chart(df['VRP'].tail(250))

st.subheader('FVRP')
st.line_chart(df['FVRP'].tail(250))
