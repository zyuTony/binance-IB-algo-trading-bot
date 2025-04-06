import os
import math
import time
from dotenv import load_dotenv
import pandas as pd
from utils.ib_utils import ib_candle_transformation
import warnings
from ib_insync import *
import numpy as np

"""
1. log on TWS 
2. run 
ib = IB()
ib.connect('127.0.0.1', 7496, clientId=1)
to connect
3. do things
"""

start_time = time.time()

# Time the connection step
connect_start = time.time()
ib = IB()
ib.connect('127.0.0.1', 7496, clientId=1) 
connect_end = time.time()
connect_time = connect_end - connect_start
print(f"IB connection time: {connect_time:.6f} seconds")

def ib_candle_to_pd_df(candle_data):
    if not candle_data:
        return pd.DataFrame()
        
    # Time the attribute extraction
    attr_start = time.time()
    sample_entry = candle_data[0]
    attributes = [attr for attr in dir(sample_entry) if not attr.startswith('_') and not callable(getattr(sample_entry, attr))]
    attr_end = time.time()
    
    # Time the data extraction loop
    loop_start = time.time()
    output = []
    for entry in candle_data:
        row = {}
        for attr in attributes:
            row[attr] = getattr(entry, attr)
        output.append(row)
    loop_end = time.time()
    
    # Time the DataFrame creation
    df_start = time.time()
    output_df = pd.DataFrame(output)
    df_end = time.time()
    
    # Time the data type conversion
    convert_start = time.time()
    if 'date' in output_df.columns:
        if isinstance(output_df['date'].iloc[0], str):
            output_df['date'] = pd.to_datetime(output_df['date'])
        
    for col in output_df.columns:
        if col == 'date':
            continue
            
        try:
            output_df[col] = pd.to_numeric(output_df[col])
        except:
            pass
    convert_end = time.time()
    
    # Print timing breakdown
    print(f"  ib_candle_to_pd_df breakdown:")
    print(f"    - Attribute extraction: {attr_end - attr_start:.6f} seconds")
    print(f"    - Data extraction loop: {loop_end - loop_start:.6f} seconds")
    print(f"    - DataFrame creation: {df_end - df_start:.6f} seconds")
    print(f"    - Data type conversion: {convert_end - convert_start:.6f} seconds")
    
    return output_df

def fast_ib_candle_to_arrays(candle):
    # Time the array initialization
    init_start = time.time()
    n = len(candle)
    ohlcv = np.zeros((n, 5))
    dates = np.zeros(n, dtype='datetime64[ms]')
    init_end = time.time()
    
    # Time the data extraction loop
    loop_start = time.time()
    for i, bar in enumerate(candle):
        dates[i] = np.datetime64(bar.date)
        ohlcv[i, 0] = float(bar.open)
        ohlcv[i, 1] = float(bar.high)
        ohlcv[i, 2] = float(bar.low)
        ohlcv[i, 3] = float(bar.close)
        ohlcv[i, 4] = float(bar.volume)
    loop_end = time.time()
    
    # Time the DataFrame creation
    df_start = time.time()
    result_df = pd.DataFrame({
        'date': dates,
        'open': ohlcv[:, 0],
        'high': ohlcv[:, 1],
        'low': ohlcv[:, 2],
        'close': ohlcv[:, 3],
        'volume': ohlcv[:, 4]
    })
    df_end = time.time()
    
    # Print timing breakdown
    print(f"  fast_ib_candle_to_arrays breakdown:")
    print(f"    - Array initialization: {init_end - init_start:.6f} seconds")
    print(f"    - Data extraction loop: {loop_end - loop_start:.6f} seconds")
    print(f"    - DataFrame creation: {df_end - df_start:.6f} seconds")
    
    return result_df

# Create contract for AAPL
# Create a contract for GAP stock
ticker = 'GAP'
exchange = 'SMART'
currency = 'USD'
contract = Stock(ticker, exchange, currency)
 
# Time the data request
request_start = time.time()
""" 30 Y of daily data works! 10Y of 1 hour data works! otherwise it goes over 60 seconds timeout"""
aapl_data = ib.reqHistoricalData(
    contract,
    endDateTime='',
    durationStr='15 Y',
    barSizeSetting='1 hour',
    whatToShow='TRADES',
    useRTH=True,
    formatDate=1) 
request_end = time.time()
request_time = request_end - request_start
print(f"IB data request time: {request_time:.6f} seconds")
print(f"Retrieved {len(aapl_data)} bars of data")

# Time the first method
method1_start = time.time()
aapl_df1 = ib_candle_to_pd_df(aapl_data)
method1_end = time.time()
method1_time = method1_end - method1_start
print(f"Method 1 (ib_candle_to_pd_df) execution time: {method1_time:.6f} seconds")

# Time the second method
method2_start = time.time()
aapl_df2 = fast_ib_candle_to_arrays(aapl_data)
method2_end = time.time()
method2_time = method2_end - method2_start
 

# Use the faster method's result
aapl_df = aapl_df2 if method2_time < method1_time else aapl_df1

# Display the data
print(f"Retrieved {len(aapl_df)} days of {ticker} data")
print("First 5 rows:")
print(aapl_df.head())
print("\nLast 5 rows:")
print(aapl_df.tail())

end_time = time.time()
execution_time = end_time - start_time
print(f"\nTotal execution time: {execution_time:.2f} seconds")
print(f"Time breakdown:")
print(f"  - Connection: {connect_time:.2f} seconds ({connect_time/execution_time*100:.1f}%)")
print(f"  - Data request: {request_time:.2f} seconds ({request_time/execution_time*100:.1f}%)")
print(f"  - Data processing: {(method1_time + method2_time):.2f} seconds ({(method1_time + method2_time)/execution_time*100:.1f}%)")
print(f"  - Other operations: {(execution_time - connect_time - request_time - method1_time - method2_time):.2f} seconds ({(execution_time - connect_time - request_time - method1_time - method2_time)/execution_time*100:.1f}%)")
