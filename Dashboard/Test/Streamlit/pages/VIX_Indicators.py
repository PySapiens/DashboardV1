# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 13:10:41 2023

@author: mydea
"""
import yfinance as yf
import pandas as pd
import quandl
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
key='3NXCnuBDyDnnhec-yWs8' #nasdaq auth
import streamlit as st

sp_df = yf.download('^GSPC')

#symbols = ('^VIX9D', '^VIX', '^VIX3M', '^VIX6M') #VIX, VIX9D, VIX3M, VIX6M, VXO (sp100), VXN (nasdaq), RVX (russel), TYVIX (10y note)
symbols = ('^VIX', '^VIX3M','^GSPC')

prices = []
for symbol in symbols:
    prices.append(yf.download(symbol, start='1990-01-01')['Adj Close'])
    prices = [price.replace('Adj Close', symbol) for price in prices]
    #print(symbol)

sig_df = pd.concat(prices, axis=1)
sig_df = sig_df.set_axis(symbols, axis=1, inplace=False).dropna()

#indicators
sig_df['VRATIO'] = sig_df['^VIX3M']/sig_df['^VIX'] #contango/bwd in cash contracts
sig_df['CTNGO'] = (quandl.get("CHRIS/CBOE_VX1", authtoken=key)['Close'])/(quandl.get("CHRIS/CBOE_VX2", authtoken=key)['Close'])
sig_df['RVOLA'] = sig_df['^GSPC'].pct_change().rolling(30).std()*(252**0.5)*100 #realized volatility
sig_df['RVOLA5'] = sig_df['^GSPC'].pct_change().rolling(5).std()*(252**0.5)*100 #realized volatility
sig_df['RVOLA10'] = sig_df['^GSPC'].pct_change().rolling(10).std()*(252**0.5)*100 #realized volatility
sig_df['VRP'] = sig_df['^VIX'] - sig_df['RVOLA10'] #vola risk premium
sig_df['VRP5'] = sig_df['VRP'].rolling(10).mean() #vrp 5 day ma
sig_df['FVRP'] = (sig_df['^VIX'].ewm(span=7, adjust=False).mean()) - sig_df['RVOLA5'] #fast vola risk premium
sig_df['VIXEMA'] = sig_df['^VIX'].ewm(span=7, adjust=False).mean()

st.subheader('VRATIO')
st.line_chart(sig_df['VRATIO'].tail(250))

st.subheader('VRP')
st.line_chart(sig_df['VRP'].tail(250))

st.subheader('FVRP')
st.line_chart(sig_df['FVRP'].tail(250))
