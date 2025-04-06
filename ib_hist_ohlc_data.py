import os
import math
from dotenv import load_dotenv
import pandas as pd
from utils.ib_utils import ib_candle_transformation
import warnings
from ib_insync import *

"""
1. log on TWS 
2. run 
ib = IB()
ib.connect('127.0.0.1', 7496, clientId=1)
to connect
3. do things
"""

ib = IB()
ib.connect('127.0.0.1', 7496, clientId=1)

# Create contract for AAPL
contract = Stock('AAPL', 'SMART', 'USD')

# Request historical data for AAPL for the last 30 days with daily timeframe
""" 30 Y of daily data works!"""
aapl_data = ib.reqHistoricalData(
    contract,
    endDateTime='',
    durationStr='30 Y',
    barSizeSetting='1 day',
    whatToShow='TRADES',
    useRTH=True,
    formatDate=1)
print(aapl_data[1])

# Transform the data to a pandas DataFrame
aapl_df = ib_candle_transformation(aapl_data)

# Display the data
print(f"Retrieved {len(aapl_df)} days of AAPL data")
print("First 5 rows:")
print(aapl_df.head())
print("\nLast 5 rows:")
print(aapl_df.tail())
