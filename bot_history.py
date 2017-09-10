'''
Created on Sep 2, 2017

@author: ricardo
'''
import time
import datetime
from dateutil import parser  # covenient lib to manipulate dates
import logging
from poloniex import PoloniexPublic
import pandas as pd
import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# import matplotlib.ticker as mticker
from matplotlib.finance import candlestick2_ohlc
# from matplotlib.dates import DateFormatter
from matplotlib import style
# import plotly.plotly as py
# import plotly.graph_objs as go
from strategy import kissBB

style.use('ggplot')
logging.basicConfig(filename='strategy.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

   
class ledger:     # #this class holds the bot transactions. It also keeps track of open position (ongoingOrder = True) and its price (purchasePrice)
    def __init__(self):
        self.ledger = []    # list of dictionaries  [{'date': date, 'type': 'buy/sell', 'price' : price}]
        self.ongoingOrder = False
        self.purchasePrice = 0
 
    def write (self, newEntry):     # this function adds an entry to the transaction ledger
        self.ledger = self.ledger + newEntry
        
    def setPurchaseprice (self, purchasePrice): # this function sets the purchasePrice of our last open position
        self.purchasePrice = purchasePrice
        
    def setOngoingorder (self, ongoingOrder):   # ongoingOrder=True means we have an open position, which we are looking to close. If False, then no open posotions
        self.ongoingOrder = ongoingOrder

        
def readInputvariables():   # this function reads the input variables from file botConfig.cfg.
    try:
        filename = './botConfig.cfg'
        fileObj = open(filename)
        var = {}
        for line in fileObj:
            line = line.strip()
            if not line.startswith('#'):
                key_value = line.split('=')
                if len(key_value) == 2:
                    var[key_value[0].strip()] = key_value[1].strip()
        
        var['pair'] = str(var['pair'])
        var['exchange'] = str(var['exchange'])
        start = parser.parse(var['start'])              # start is now DateTime format
        var['start'] = time.mktime(start.timetuple())   # now converted into unix time
        end = parser.parse(var['end'])                  # end is now DateTime format
        var['end'] = time.mktime(end.timetuple())       # now converted into unix time       
        if  var['end'] <= var['start']:
            print var['end'], ' needs to be later than ', var['start']
            exit(0)   
        var['period'] = int(var['period'])
        if var['period'] not in [300, 900, 1800, 7200, 1440, 86400]:  
            print var['period'], ' must be one of 300, 900, 1800, 7200, 14400, and 86400' 
            exit(0)
        var['kissLow'] = int(var['kissLow'])
        var['kissMA'] = int(var['kissMA'])
        var['kissHigh'] = int(var['kissHigh'])
        var['kissStoploss'] = float(var['kissStoploss'])        
        return var
                 
    except Exception, e:
        print 'something wrong on the configuration file: wrong variables ', str(e)
   

def pullData(pair, period, uStart, uEnd):   # this function retrieves data from the exchange
    try:
        print uStart, uEnd
        pol = PoloniexPublic()

        # dataAPI = pol.returnTradeHistory(pair)  -> returns last 200 history entries 
        dataAPI = pol.returnChartData(pair, period, uStart, uEnd)  # returns entries between two dates, at the given period:300, 900, 1800 (sec)
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


# ## start the program

if __name__ == '__main__':

    var = readInputvariables()              # reads input variables from file
                                            # fetches data from the exchange
    data = pullData(var['pair'], var['period'], var['start'], var['end'])
    dataF = analysis(data)                  # calculates technical analysis on the fetched data
    ledger = ledger()                       # instantiates the ledger
        
    i = 0
    while i < len(dataF):
        if i >= 20:
            trade = kissBB(dataF.ix[i - 20:i], ledger, i, var)   # feeds the last 20 entries to the kissBB strategy, skips the first 20 (need at least 20 for MA)    
        logging.info('i={0} \n{1}'.format(i, dataF.loc[i]))
        i = i + 1
    
    df = pd.DataFrame(ledger.ledger)               
    print df
    print 'profit', df['profit'].sum()
    
    graphStock(dataF, var['pair'])
    
    # trade(dataF.ix[20])
    # dataF.plot(x='date', y='weightedAverage')
    # plt.show()
