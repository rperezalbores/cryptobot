'''
Created on Sep 2, 2017

@author: ricardo
'''
import time
import datetime
import logging
import numpy as np
from poloniex import Poloniex, PoloniexPublic

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.finance import candlestick2_ohlc
from matplotlib.dates import DateFormatter
from matplotlib import style
import plotly.plotly as py
import plotly.graph_objs as go
from trade_history import trade_history, kissBB

        
class ledger:
    def __init__(self):
        self.ledger = []    # [{'date': date, 'type': 'buy/sell', 'price' : price}]
        self.ongoingOrder = False
        self.purchasePrice = 0
 
    def write (self, newEntry):
        self.ledger = self.ledger + newEntry
        
    def setPurchaseprice (self, purchasePrice):
        self.purchasePrice = purchasePrice
        
    def setOngoingorder (self, ongoingOrder):
        self.ongoingOrder = ongoingOrder

        
        
    
    
style.use('ggplot')
logging.basicConfig(filename='trade_history.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')


def pullData(pair, period, uStart, uEnd):
    try:
        pol = PoloniexPublic()

        # dataAPI = pol.returnTradeHistory(pair)  -> returns history
        dataAPI = pol.returnChartData(pair, period, uStart, uEnd)
        print dataAPI
        df = pd.DataFrame(dataAPI)
        df['date'] = pd.to_datetime(df['date'], unit='s')  # converts UNIX dates returned by Poloniex into human readable dates

        print 'Pulled ' + str(len(df)) + ' samples of', pair, period
        print 'sleeping'
        time.sleep(1)
        return df

    except Exception, e:
        print 'pull Data ', str(e)


def analysis(ds):
    try:
        ds['20d_ma'] = ds['close'].rolling(window=20).mean()
        ds['50d_ma'] = ds['close'].rolling(window=50).mean()
        ds['Bol_upper'] = ds['close'].rolling(window=20).mean() + 2 * ds['close'].rolling(20, min_periods=20).std()
        ds['Bol_lower'] = ds['close'].rolling(window=20).mean() - 2 * ds['close'].rolling(20, min_periods=20).std()
        ds['Bol_BW'] = ((ds['Bol_upper'] - ds['Bol_lower']) / ds['20d_ma']) * 100
        ds['Bol_BW_200MA'] = ds['Bol_BW'].rolling(window=50).mean()  # cant get the 200 daa
        ds['Bol_BW_200MA'] = ds['Bol_BW_200MA'].fillna(method='backfill')  # ?? ,may not be good
        # ds['20d_exma'] = ds['close'].ewm(span=20)
        # ds['50d_exma'] = ds['close'].ewm(span=50)
        # data_ext.all_stock_df = ds.sort('date', ascending=False)  # revese back to original

        return ds

    except Exception, e:
        print 'analysis ', str(e)


def graphStock(df, pair):
    try:
        fig = plt.figure()
        ax = plt.subplot2grid((1, 1), (0, 0))

        candlestick2_ohlc(ax, df['open'], df['high'], df['low'], df['close'], width=0.6, colorup='#69f212', colordown='#E6323D')
        ax.plot(df['20d_ma'], linestyle='-', label='20d sma')
        ax.plot(df['Bol_upper'], linestyle='-', label='Boll upper')
        ax.plot(df['Bol_lower'], linestyle='-', label='Boll lower')

        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(pair)
        plt.legend()

        ax.xaxis.grid(True, 'major')
        ax.xaxis.grid(False, 'minor')
        ax.grid(True)
        plt.show()

    except Exception, e:
        print 'graphStock ', str(e)



pair = 'USDT_BTC'
start = datetime.date(2017, 9, 1)
end = datetime.date(2017, 9, 3)
uStart = time.mktime(start.timetuple())
uEnd = time.mktime(end.timetuple())

data = pullData(pair, 300, uStart, uEnd)
dataF = analysis(data)
ledger = ledger()

i = 0
while i < len(dataF):
    if i >= 20:
        trade = kissBB(dataF.ix[i - 20:i], ledger, i)
        if trade:
            print i
 
    logging.info('i={0} \n{1}'.format(i, dataF.loc[i]))
    i = i + 1

df = pd.DataFrame(ledger.ledger)        
print df
print 'profit', df['profit'].sum()

graphStock(dataF, pair)

# trade(dataF.ix[20])
# dataF.plot(x='date', y='weightedAverage')
# plt.show()
