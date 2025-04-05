# Trading Logic

import pandas as pd
from datetime import datetime

class TradePackage:
    def __init__(self, ticker_name="AAPL", trade_type="long"):
        self.ticker_name = ticker_name
        self.strategy = Strategy()
        self.open_time = None
        self.close_time = None
        self.trade_id = f"{self.ticker_name}_{self.strategy.name}_{self.timestamp}"
        self.status = 'to_open'  # 'to_open', 'open', or 'closed'
        self.open_price = None
        self.close_price = None
        self.type = trade_type  # 'long' or 'short'
        self.profit_loss = None

    def open_trade(self, price):
        self.open_price = price
        self.status = 'open'
        print(f"Trade opened: {self.trade_id} at {price}")
        
    def close_trade(self, price):
        self.close_price = price
        self.status = 'closed'
        self.calculate_profit_loss()
        print(f"Trade closed: {self.trade_id} at {price}")
        
    def calculate_profit_loss(self):
        if self.open_price and self.close_price:
            if self.type == 'long':
                self.profit_loss = (self.close_price - self.open_price) / self.open_price
            else:  # short
                self.profit_loss = (self.open_price - self.close_price) / self.open_price
        
    def tick(self, current_price):
        # check whether closing condition is met
        if self.status == 'open' and self.strategy.closing_condition(current_price):
            self.close_trade(current_price)

class Strategy:
    def __init__(self, name="default_strategy"):
        self.name = name
        self.indicators = Indicators()
        self.data = OHLCData()
        
    def opening_condition(self, price):
        # Example: SMA > price and EMA < price
        sma = self.indicators.SMA(20)
        ema = self.indicators.EMA(14)
        
        if sma and ema:
            return sma > price and ema < price
        return False
        
    def closing_condition(self, price):
        # Example: Take profit or stop loss
        if self.data.last_price:
            profit_pct = (price - self.data.last_price) / self.data.last_price
            return profit_pct > 0.05 or profit_pct < -0.03
        return False

class Indicators:
    def __init__(self):
        self.data = None
    
    def set_data(self, data):
        self.data = data
    
    def SMA(self, length):
        if self.data is not None and len(self.data) >= length:
            return self.data['close'].rolling(window=length).mean().iloc[-1]
        return None
        
    def EMA(self, length):
        if self.data is not None and len(self.data) >= length:
            return self.data['close'].ewm(span=length, adjust=False).mean().iloc[-1]
        return None

class OHLCData:
    '''this is a dataset that contains OHLC data'''
    def __init__(self, ticker_name='AAPL', timeframe='1m', data_path='data.csv'):
        try:
            self.data = pd.read_csv(data_path)
            self.ticker_name = ticker_name
            self.timeframe = timeframe
            self.last_price = self.data['close'].iloc[-1] if not self.data.empty else None
        except Exception as e:
            print(f"Error loading data: {e}")
            self.data = pd.DataFrame()
            self.last_price = None
    
    def update_data(self, new_data):
        self.data = pd.concat([self.data, new_data]).reset_index(drop=True)
        self.last_price = self.data['close'].iloc[-1] if not self.data.empty else None
"""
Data Housekeeping:
- ingest data from data source
- store in some way


Actual Trade Process:
- Set up
  - pick tickers to trade
  - pick stragegy active time
  - pick strategy
  trade_package = {tickers: "AAPL", strat: "simple_SMA", active_time: "9:30AM-10:00AM", monitor_freq: "5m"}
  strategy = {name: "simple_SMA", params: {SMA_length: 50}, size: 1000}
  
- Opening:
  - Gather data for traded stock.
  - Calculate indicatorsr/signals. For example, SMA, EMA, ATR, VWAP.
  - create trade_package instance with status "to_open" and trade_id.
  - Check whether opening condition met every monitor_freq.
  - If condition met, open the trade and add a trade package instance with status "open" and trade_id.
  - Record open_time, open_price, size, $ size

-Closing:
  - Find all trade_package instances with status "open".
  - Check whether closing condition met every monitor_freq.
  - If condition met, close the trade.
  - Record close_time, close_price, size, $ size
  
Performance Backtesting:
- determine what data to test. For example,
  - select tickers with market cap over 100M and in retail sector. Like Nike, TJX, etc.
  - select tickers with average daily volume past 30 days over 10M.
  - select month/week/daytime to trade. For example, 2 hours after market open. In April before Option expiration. 
  - select data duration. For example, use past 3 years of data.
  - mark the selected market trend. For example, a bull, bear or flat market.
  - mark the volatility of the selected market.

- determine strategy
  - opening condition
    - pick time of day/month of year. First hour of Friday. Every April. End of Year. 
    - pick timeframe of data. OHLC data of 15m bar. Vol of daily bar.
    - pick timeframe of indicator. SMA50 of 1d bar. SMA20w of weekly bar.
    - pick indicator. SMA, EMA, ATR, VWAP.
    - pick opening condition. SMA > price and EMA < price.
    - pick opening size. 50% of account. 10% of account.
    
    
  - closing condition
    - stop loss
      - sell when reaches fixed price. Loss has reached 5% or more.
      - sell when reaches max trade duration. Trade lasted more than 2 weeks or other expected duration.
    - take profit
      - sell when reaches fixed price. Profit has reached 5% or more.
      - sell when reaches max trade duration. Trade lasted more than 2 weeks or other expected duration.

- determine metrics to backtest and evaluate
    - Gross Profit/Gross Loss
    - Pareto Index - check whether profit come from few or many trades.
    - Calmar Ratio - (total return - risk free rate)/max drawdown
    - Expected Value - Win Rate * Average Win Size - Loss Rate * Average Loss Size
    
"""