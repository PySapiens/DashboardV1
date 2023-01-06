import streamlit as st
import pandas as pd
import sqlalchemy
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
from fredapi import Fred
fred_key = ''
#import ta
import yfinance as yf
from sqlalchemy import create_engine
from datetime import datetime

#Data and Database
engine = create_engine('sqlite:///Database.db')
start = '1990-01-01'
fred_ids = ['WALCL','WTREGEN', 'RRPONTSYD', 'SP500']
vix_ids = ['^VIX', '^VIX3M','^GSPC']
yf_ids = vix_ids + []

#DB Importer FRED
def fred_downloader(id, start):
    fred = Fred(api_key=fred_key)
    fred_df = fred.get_series(series_id=id, observation_start=start)
    return fred_df

def sql_importer_fred(symbol, start):
    try:
        max_date = str(pd.read_sql(symbol, engine).set_index('index').index[-1].date())
        #max_date = pd.read_sql(f'SELECT MAX(index) FROM {symbol}', engine).values[0][0]
        print(max_date)
        new_data = fred_downloader(symbol, start=pd.to_datetime(max_date))
        #new_data = yf.download(symbol, start=pd.to_datetime(max_date))
        new_rows = new_data[new_data.index > max_date]
        new_rows.to_sql(symbol, engine, if_exists='append')
        print(str(len(new_rows)) + ' new rows imported to DB')
    except:
        new_data = fred_downloader(symbol, start=start)
        new_data.to_sql(symbol, engine)
        print(f'New table created for {symbol} with {str(len(new_data))} rows')

#DB Importer Yfinance
def sql_importer_yf(symbol, start):
    try:
        max_date = str(pd.read_sql(symbol, engine).set_index('Date').index[-1].date())
        #max_date = pd.read_sql(f'SELECT MAX(Date) FROM {symbol}', engine).values[0][0]
        print(max_date)
        new_data = yf.download(symbol, start=pd.to_datetime(max_date))#['Adj Close'].replace('Adj Close', symbol)
        new_rows = new_data[new_data.index > max_date]
        new_rows.to_sql(symbol, engine, if_exists='append')
        print(str(len(new_rows)) + ' new rows imported to DB')
    except:
        new_data = yf.download(symbol, start=start)
        new_data.to_sql(symbol, engine)
        print(f'New table created for {symbol} with {str(len(new_data))} rows')


#FRED Calculations
all_results = []
for id in fred_ids:
    results = pd.read_sql(id, engine).set_index('index')
    all_results.append(results)
fred_df = pd.concat(all_results, axis=1)
fred_df = fred_df.fillna(method='bfill')
fred_df = fred_df.fillna(method='ffill')
fred_df = fred_df.dropna()
fred_df.columns = fred_ids
fred_df['NET_LIQ'] = (fred_df.WALCL - fred_df.WTREGEN * 1000 - fred_df.RRPONTSYD * 1000)/(1000*1000)
fred_df['SP_FV'] = fred_df.SP500 - ((fred_df.WALCL - fred_df.WTREGEN * 1000 - fred_df.RRPONTSYD * 1000)/1000/1.1-1625)

#VIX Calculations
vix_all_results = []
for id in vix_ids:
    results = pd.read_sql(id, engine).set_index('Date')
    results = results['Adj Close']
    vix_all_results.append(results)
vix_df = pd.concat(vix_all_results, axis=1)
vix_df = vix_df.fillna(method='bfill')
vix_df = vix_df.fillna(method='ffill')
vix_df = vix_df.dropna()
vix_df.columns = vix_ids

#VIX Indicators
vix_df['VRATIO'] = vix_df['^VIX3M']/vix_df['^VIX'] #contango/bwd in cash contracts
#df['CTNGO'] = (quandl.get("CHRIS/CBOE_VX1", authtoken=key)['Close'])/(quandl.get("CHRIS/CBOE_VX2", authtoken=key)['Close'])
vix_df['RVOLA'] = vix_df['^GSPC'].pct_change().rolling(30).std()*(252**0.5)*100 #realized volatility
vix_df['RVOLA5'] = vix_df['^GSPC'].pct_change().rolling(5).std()*(252**0.5)*100 #realized volatility
vix_df['RVOLA10'] = vix_df['^GSPC'].pct_change().rolling(10).std()*(252**0.5)*100 #realized volatility
vix_df['VRP'] = vix_df['^VIX'] - vix_df['RVOLA10'] #vola risk premium
vix_df['VRP5'] = vix_df['VRP'].rolling(10).mean() #vrp 5 day ma
vix_df['FVRP'] = (vix_df['^VIX'].ewm(span=7, adjust=False).mean()) - vix_df['RVOLA5'] #fast vola risk premium
vix_df['VIXEMA'] = vix_df['^VIX'].ewm(span=7, adjust=False).mean()

#STREAMLIT
col1, col2, col3 = st.columns(3)
if col3.button('Update DB'):
    #Update Fred
    for id in fred_ids:
        sql_importer_fred(id, start)
        print(id + ' imported')
    #Update YF
    for id in yf_ids:
        sql_importer_yf(id, start)
        print(id + ' imported')
    col3.write('DB updated: ' + str(datetime.today().date()))
#else:
    #col3.write('ERROR updating DB')

st.header('Overview')

st.subheader('NL and FV Indicators')
st.caption('Last timestamp: '  + str(fred_df.index[-1].date()))
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(label="Fair Value", value=round(fred_df['SP_FV'][-1], 0), delta=round((fred_df['SP_FV'][-1])-fred_df['SP_FV'][-5], 0), help="vs. value last week")
col2.metric(label="Net Liquidity", value=round(fred_df['NET_LIQ'][-1], 3), delta=round(fred_df['NET_LIQ'][-1]-fred_df['NET_LIQ'][-5], 3), help="vs. value last week")
col3.metric(label="WALCL", value=round(fred_df['WALCL'][-1], 0), delta=round(fred_df['WALCL'][-1]-fred_df['WALCL'][-5], 0), help="vs. value last week")
col4.metric(label="WTREGEN", value=round(fred_df['WTREGEN'][-1], 0), delta=round(fred_df['WTREGEN'][-1]-fred_df['WTREGEN'][-5], 0), help="vs. value last week")
col5.metric(label="RRPONTSYD", value=round(fred_df['RRPONTSYD'][-1], 0), delta=round(fred_df['RRPONTSYD'][-1]-fred_df['RRPONTSYD'][-5], 0), help="vs. value last week")

st.subheader('VIX Indicators')
st.caption('Last timestamp: '  + str(vix_df.index[-1].date()))
col1, col2, col3 = st.columns(3)
col1.metric(label="VRATIO", value=round(vix_df['VRATIO'][-1], 3), delta=round((vix_df['VRATIO'][-1])-vix_df['VRATIO'][-5], 3), help="vs. value last week - VRatio > 1: Risk-On signal")
col2.metric(label="VRP", value=round(vix_df['VRP'][-1], 3), delta=round(vix_df['VRP'][-1]-vix_df['VRP'][-5], 3), help="vs. value last week - VRP > 0: Risk-On signal")
col3.metric(label="FVRP", value=round(vix_df['FVRP'][-1], 3), delta=round(vix_df['FVRP'][-1]-vix_df['FVRP'][-5], 3), help="vs. value last week - FVRP > 0: Risk-On signal")

#VRATIO, VRP, FVRP
