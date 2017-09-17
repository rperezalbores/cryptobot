'''
Created on Sep 2, 2017

@author: ricardo
'''
import time
import datetime
from dateutil import parser  # covenient library to manipulate dates
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
from strategy import analysis, tannous, kissBB

style.use('ggplot')
logging.basicConfig(filename='strategy.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

   
class ledger:     # this class holds the bot transactions. It also keeps track of open position (ongoingOrder = True) and its price (purchasePrice)
    def __init__(self):
        self.ledger = []                        # list of dictionaries  [{'date': date, 'type': 'buy/sell', 'price' : price}]
        self.ongoingOrder = False
        self.purchasePrice = 0
 
    def write (self, newEntry):                 # this function adds an entry to the transaction ledger
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
        var['mode'] = str(var['mode'])
        var['polling'] = int(var['polling'])
        var['candleStickperiod'] = int(var['candleStickperiod'])
        start = parser.parse(var['start'])              # start is now DateTime format
        var['start'] = time.mktime(start.timetuple())   # now converted into unix time
        end = parser.parse(var['end'])                  # end is now DateTime format
        var['end'] = time.mktime(end.timetuple())       # now converted into unix time       
        if  var['end'] <= var['start']:
            print var['end'], ' needs to be later than ', var['start']
            exit(0)   
        var['period'] = int(var['period'])
        if var['period'] not in [300, 900, 1800, 7200, 1440, 86400]:  
            print var['period'], ' must be one of these values: 300, 900, 1800, 7200, 14400, and 86400' 
            exit(0)
        var['strategy'] = str(var['strategy'])
        var['kissLow'] = int(var['kissLow'])
        var['kissMA'] = int(var['kissMA'])
        var['kissHigh'] = int(var['kissHigh'])
        var['Stoploss'] = float(var['Stoploss'])        
        return var
                 
    except Exception, e:
        print 'something wrong on the configuration file: wrong variables ', str(e)
   

def connectExchange(exchange):                 # this function connects to the exchange and returns its handle
    try:
        if exchange == 'Poloniex':
            # connects to Poloniex public API
            return PoloniexPublic()
        elif exchange == 'Bittrex':
            # connects to Bittrex - to be implemented
            pass
        else:
            print 'Error connecting to exchange. Check botConfig.cfg file and make sure the exchange is spelt correctly'
    except Exception, e:
        print 'connectExchange ', str(e)

def pullRealtime(pair, exchangeHandle):        # this function retrieves real time data and returns a dataset
    try:
        dataAPI = exchangeHandle.returnTicker()                 # grabs ticker from exchange
        dataPair = dataAPI[pair]                                # select the pair we are interested in
        df = pd.DataFrame([dataPair], columns=dataPair.keys())  # imports data (dictionary type) into panda dataset
        return df                                               # returns dataset

    except Exception, e:
        print 'pullRealtime ', str(e)

def createCandle(rawData):                     # this function returns a candlestick based on real time data 
    try:
        high = rawData['last'].max()                # maximum of this period
        volume = rawData['quoteVolume'].mean()      # volumen average
        low = rawData['last'].min()                 # minimum of this period
        date = str(datetime.datetime.now())
        close = rawData['last'].iloc[-1]            # closing price
        # weightedAverage = rawData['last'].mean()
        opend = rawData['last'].iloc[0]             # open price

        candle = [{'date': date, 'open': opend, 'high': high,
                   'low': low, 'close': close, 'volume': volume}]
        return candle

    except Exception, e:
        print 'createCandle', str(e)

def pullHistory(pair, period, uStart, uEnd):   # this function retrieves historical data from the exchange between two dates. Returns panda dataframe
    try:
        print uStart, uEnd
        pol = PoloniexPublic()                                      # connects to Poloniex

        dataAPI = pol.returnChartData(pair, period, uStart, uEnd)   # returns entries between two dates, at the given period:300, 900, 1800 (sec)
        df = pd.DataFrame(dataAPI)                                  # coverts retrieved data from Poloniex into a dataframe
        df['date'] = pd.to_datetime(df['date'], unit='s')           # converts UNIX dates returned by Poloniex into human readable dates
        print 'Pulled ' + str(len(df)) + ' samples of', pair, period
        return df

    except Exception, e:
        print 'PullHistory', str(e)

def graphHistory(df, var):                    # this function graphs historical data
    try:
        # fig = plt.figure()
        ax = plt.subplot2grid((1, 1), (0, 0))

        candlestick2_ohlc(ax, df['open'], df['high'], df['low'], df['close'], width=0.6, colorup='#69f212', colordown='#E6323D')
        if var['strategy'] == 'kissBB':
            ax.plot(df['20d_ma'], linestyle='-', label='20d sma')
            ax.plot(df['Bol_upper'], linestyle='-', label='Boll upper')
            ax.plot(df['Bol_lower'], linestyle='-', label='Boll lower')          
        elif var['strategy'] == 'tannous':
            ax.plot(df['20d_ma'], linestyle='-', label='20d sma')
            ax.plot(df['Bol_upper_22'], linestyle='-', label='Boll upper 22')
            ax.plot(df['Bol_lower_22'], linestyle='-', label='Boll lower 22')
            ax.plot(df['Bol_upper_30'], linestyle='-', label='Boll upper 30')
            ax.plot(df['Bol_lower_30'], linestyle='-', label='Boll lower 30')
 
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(var['pair'])
        plt.legend()

        ax.xaxis.grid(True, 'major')
        ax.xaxis.grid(False, 'minor')
        ax.grid(True)
        plt.show()

    except Exception, e:
        print 'graphStock ', str(e)


# ## start the program

if __name__ == '__main__':

    var = readInputvariables()                                                      # reads input variables from file
    ledger = ledger()                                                               # instantiates the ledger
    logging.info('starting bot mode {0}'.format(var['mode']))
    print var
    
    if var['mode'] == 'history':                    
        data = pullHistory(var['pair'], var['period'], var['start'], var['end'])    # fetches historic data from the exchange between dates
        dataF = analysis(data)                                                      # calculates technical analysis on the fetched data
        print 'entering mode history'
        print len(dataF)
        print dataF
        i = 0
        while i < len(dataF):
            if i >= 20:
                if var['strategy'] == 'tannous':
                    trade = tannous(dataF.ix[i - 20:i], ledger, i, var)  # feeds the last 20 entries to hannous strategy, skips the first 20 (need at least 20 for MA)    
                elif var['strategy'] == 'kissBB':
                    trade = kissBB(dataF.ix[i - 20:i], ledger, i, var)   # feeds the last 20 entries to kissBB strategy, skips the first 20 (need at least 20 for MA)    
                else:
                    print ('Error in strategy, make sure it is spelt correctly')   
                    exit(0)
            # logging.info('i={0} \n{1}'.format(i, dataF.loc[i]))
            i = i + 1
        
        df = pd.DataFrame(ledger.ledger)                                 # transforms ledger in a panda dataframe for easy analysis
        print 'printing final results'
        print df
        logging.info(df)
        print 'profit', df['profit'].sum()
        logging.info('profit {0}'.format(df['profit'].sum()))
        graphHistory(dataF, var)
    
    elif var['mode'] == 'realtime':
        exchangeHandle = connectExchange(var['exchange'])                           # connects to exchange
        logging.info('connected to ' + var['exchange'] + ' pulling data')           # logs connection
        realtimeData = pullRealtime(var['pair'], exchangeHandle)                    # initializes dataframe
        candles = []                                                                # initializes our data structure
    
        i = 0
        while True:
            
            try:
                realtimeData = pd.concat((realtimeData, pullRealtime(var['pair'], exchangeHandle)), ignore_index=True)       # pulls last price from exchange and appends it to the dataframe
                i = i + 1
                if i == var['candleStickperiod']:                                       # is it time to create a new candle?
                    newCandle = createCandle(realtimeData)                              # create new candle
                    candles = candles + newCandle                                       # adds the new candle to the candle list
                    candlesDF = pd.DataFrame(candles)                                   # create dataframe ready for technical analysis
                    candlesTAdf = analysis(candlesDF)                                   # runs technical analysis calculations on the candle data
                    if var['strategy'] == 'tannous':
                        trade = tannous(candlesTAdf, ledger, i, var)                    # go hannous go
                    elif var['strategy'] == 'kissBB':
                        trade = kissBB(candlesTAdf, ledger, i, var)                     # go make some money
                    else:
                        print ('Error in strategy, make sure it is spelt correctly on botConfig.cfg file')   
                        exit(0)
                    i = 0                                                               # reset the period, ready for a new candle
                    realtimeData = realtimeData.ix[-1:-2]                               # flushes the real time data, ready for a new candle
                    if trade:                                                           # is there a new trade? if so, lets show some results
                        df = pd.DataFrame(ledger.ledger)                                # transforms ledger in a dataframe for easy analysis
                        print df
                        logging.info(df)
                        print 'profit', df['profit'].sum()
                        logging.info('profit {0}'.format(df['profit'].sum()))
                        
                if len(candles) > 100:
                    candles = candles[1:]                                               # drops the first row, preventing candles growth to infinitum: allows 100 candles
            
            except Exception, e:
                print 'Issues connecting to Poloniex ', str(e)       
            
            # dataF = analysis(data)
            # print dataF
            # dataF.plot(x='date', y='weightedAverage')
            # plt.show()
            # polling (in seconds) determines the polling interval to the exchange
            time.sleep(var['polling'])          # this really determines the pace of queries to the exchange

    
    else:
        print ' Error in mode. Make sure mode is splet correctly'


