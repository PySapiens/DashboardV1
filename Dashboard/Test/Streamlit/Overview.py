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
from sqlalchemy import create_engine

#Databases
engine = create_engine('sqlite:///Database.db')
fred_df = pd.read_sql('WALCL',engine).set_index('index')
#vix_df = pd.read_sql('VRATIO', engine).set_index('Date')




#pages
#import sys 
#import os
#sys.path.append(os.path.abspath("D:\Programming\finance\Dashboard\Test\Streamlit\pages"))
#from Net_Liquidity import *


# Neue Übersicht, alle Indikatoren im Kurzansicht vs letzte Woche

#st.metric(label="Fair Value", value=fred_df['SP_FV'].tail(1), delta=fred_df['SP_FV'].tail(5)[-5, help='value last week'])

st.header('Overview')

st.subheader('NL and FV Indicators')
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(label="Fair Value", value=round(fred_df['SP_FV'][-1], 0), delta=round((fred_df['SP_FV'][-1])-fred_df['SP_FV'][-5], 0), help="vs. value last week")
col2.metric(label="Net Liquidity", value=round(fred_df['NET_LIQ'][-1], 3), delta=round(fred_df['NET_LIQ'][-1]-fred_df['NET_LIQ'][-5], 3), help="vs. value last week")
col3.metric(label="WALCL", value=round(fred_df['WALCL'][-1], 0), delta=round(fred_df['WALCL'][-1]-fred_df['WALCL'][-5], 0), help="vs. value last week")
col4.metric(label="WTREGEN", value=round(fred_df['WTREGEN'][-1], 0), delta=round(fred_df['WTREGEN'][-1]-fred_df['WTREGEN'][-5], 0), help="vs. value last week")
col5.metric(label="RRPONTSYD", value=round(fred_df['RRPONTSYD'][-1], 0), delta=round(fred_df['RRPONTSYD'][-1]-fred_df['RRPONTSYD'][-5], 0), help="vs. value last week")

st.subheader('VIX Indicators')
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(label="VRATIO", value=round(vix_df['VRATIO'][-1], 0), delta=round((vix_df['VRATIO'][-1])-vix_df['VRATIO'][-5], 0), help="vs. value last week")
col2.metric(label="VRP", value=round(vix_df['VRP'][-1], 3), delta=round(vix_df['VRP'][-1]-vix_df['VRP'][-5], 3), help="vs. value last week")
col3.metric(label="FVRP", value=round(vix_df['FVRP'][-1], 0), delta=round(vix_df['FVRP'][-1]-vix_df['FVRP'][-5], 0), help="vs. value last week")
col4.metric(label="FVRP", value=round(vix_df['FVRP'][-1], 0), delta=round(vix_df['FVRP'][-1]-vix_df['FVRP'][-5], 0), help="vs. value last week")
col5.metric(label="FVRP", value=round(vix_df['FVRP'][-1], 0), delta=round(vix_df['FVRP'][-1]-vix_df['FVRP'][-5], 0), help="vs. value last week")

#VRATIO, VRP, FVRP