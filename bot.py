'''
Created on Sep 2, 2017

@author: ricardo
'''


import time
import datetime
from poloniex import Poloniex, PoloniexPublic
import pandas as pd
import matplotlib.pyplot as plt
import logging
from trade import trade, test

logging.basicConfig(filename='trade.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')


def connectExchange(exchange):
    try:
        # connects to Poloniex public API
        return PoloniexPublic()

    except Exception, e:
        print 'connectExchange ', str(e)


def pullCoin(pair, exchangeHandle):
    try:
        dataAPI = exchangeHandle.returnTicker()                 # grabs ticker from exchange
        dataPair = dataAPI[pair]                                # select the pair we are interested in
        df = pd.DataFrame([dataPair], columns=dataPair.keys())  # imports data (dictionary type) into dataset
        return df

    except Exception, e:
        print 'pullCoin ', str(e)


def createCandle(rawData):
    try:
        high = rawData['last'].max()
        volume = rawData['quoteVolume'].mean()
        low = rawData['last'].min()
        date = str(datetime.datetime.now())
        close = rawData['last'].iloc[-1]
        weightedAverage = rawData['last'].mean()
        opend = rawData['last'].iloc[0]

        candle = [{'date': date, 'open': opend, 'high': high,
                   'low': low, 'close': close, 'volume': volume}]
        return candle

    except Exception, e:
        print 'createCandle', str(e)


def analysis(ds):
    try:
        ds['20d_ma'] = ds['close'].rolling(window=20).mean()
        ds['50d_ma'] = ds['close'].rolling(window=50).mean()
        ds['Bol_upper'] = ds['close'].rolling(window=20).mean() + 2 * ds['close'].rolling(20, min_periods=20).std()
        ds['Bol_lower'] = ds['close'].rolling(window=20).mean() - 2 * ds['close'].rolling(20, min_periods=20).std()
        ds['Bol_BW'] = ((ds['Bol_upper'] - ds['Bol_lower']) / ds['20d_ma']) * 100
        ds['Bol_BW_200MA'] = ds['Bol_BW'].rolling(window=50).mean()  # cant get the 200 daa
        ds['Bol_BW_200MA'] = ds['Bol_BW_200MA'].fillna(method='backfill')  # ?? ,may not be good
        ds['20d_exma'] = ds['close'].ewm(span=20)
        ds['50d_exma'] = ds['close'].ewm(span=50)
        # data_ext.all_stock_df = ds.sort('date', ascending=False)  # revese
        # back to original

        return ds

    except Exception, e:
        print 'analysis ', str(e)



if __name__ == '__main__':

    pair = 'USDT_BTC'
    exchangeName = 'Poloniex'
    
    polling = 1             # determines the polling period to the exchange in seconds
    candleStickperiod = 10  # determines how many samples to create a candlestick

    ongoingOrder = False
    purchasePrice = 0

    logging.info('starting bot ')

    exchange = connectExchange(exchangeName)                                                                    # connects to exchange
    logging.info('connected to ' + exchangeName + ' pulling data')                                              # logs connection
    df = pullCoin(pair, exchange)                                                                               # initializes dataframe
    data = [{'date': str(datetime.datetime.now()), 'open': 0, 'high': 0, 'low': 0, 'close': 0, 'volume': 0}]    # initializes our data structure

    i = 0
    while True:
        df = pd.concat((df, pullCoin(pair, exchange)), ignore_index=True)       # pulls last price from exchange and appends it to the dataframe
        i = i + 1
        if i == candleStickperiod:                                              # is it time to create a new candle?
            newCandle = createCandle(df)                                        # create new candle
            data = data + newCandle                                             # adds the new candle to the data list
            candleDF = pd.DataFrame(data)                                       # create dataframe ready for technical analysis
            ta = analysis(candleDF)                                             # ta datafram contains now the data and the technical analysis
            ongoingOrder, purchasePrice = trade(ta, ongoingOrder, purchasePrice)
            i = 0                                                               # reset the period
            df = df.ix[-1:-2]                                                   # flushes the data, ready for a new period to calculate the candle
        if len(data) > 100:
            data = data[1:]                                                     # drops the first row, preventing data growth to infinitum: allows 100 rows

        # dataF = analysis(data)
        # print dataF
        # dataF.plot(x='date', y='weightedAverage')
        # plt.show()
        # polling (in seconds) determines the polling interval to the exchange
        time.sleep(polling)
