'''
Created on Sep 2, 2017

@author: ricardo
'''

import logging
import pandas as pd


def kissBB(data, ledger, index, var):
    try:
        currentPrice = data['close'].iloc[-1]
        previousPrice = data['close'].iloc[-2]
        previousLow = data['low'].iloc[-2]
        bolLower = data['Bol_lower'].iloc[-1]
        bolUpper = data['Bol_upper'].iloc[-1]
        ma20 = data['20d_ma'].iloc[-1]
        date = data['date'].iloc[-1]
        thresholdD = bolLower + 0.2 * (ma20 - bolLower)
        thresholdU = bolUpper - 0.2 * (bolUpper - ma20)
        
        if not ledger.ongoingOrder:  
            if touchLowerBB(data, bolLower, var['kissLow']) and not maDecreasing(data, var['kissMA']):  # touched lowerBB and moving average not decreasing                                                                                    # price is increasing over the last depth periods
                logging.info('buying at {0}'.format(ledger.purchasePrice))     
                transaction = [{'date': data['date'].iloc[-1], 'type': 'buy', 'price' : currentPrice, 'profit': 0, 'explanation':'buy', 'index':index}]
                ledger.setPurchaseprice (currentPrice)
                ledger.setOngoingorder(True)
                ledger.write(transaction)
                return(True)

        if ledger.ongoingOrder:  
            stopLossprice = ((100 - var['kissStoploss']) / 100) * ledger.purchasePrice
            if currentPrice < stopLossprice:          # we are losing kissStopLoss, stop loss, we close the position
                loss = currentPrice - ledger.purchasePrice
                logging.info('sell - closing position - stop loss price {0} loss {1}'.format(currentPrice, loss))
                transaction = [{'date': data['date'].iloc[-1], 'type': 'sell', 'price' : currentPrice, 'profit' : loss, 'explanation':'stop loss', 'index':index}]
                ledger.setPurchaseprice(currentPrice)
                ledger.setOngoingorder(False)
                ledger.write(transaction)              
                return (True)
                                                                                       
            if  touchUpperBB(data, bolUpper, var['kissHigh']):                    # closing position
                profit = currentPrice - ledger.purchasePrice
                logging.info('sell price {0} profit {1} '.format(currentPrice, profit))
                transaction = [{'date': data['date'].iloc[-1], 'type': 'sell', 'price' : currentPrice, 'profit':profit, 'explanation':'hopefully profit', 'index':index}]
                ledger.setPurchaseprice(currentPrice)
                ledger.setOngoingorder(False)
                ledger.write(transaction)              
                return (True)                                                                    
        
        return(False)

    except Exception, e:
        print 'trade ', str(e)
    
    

def trade_history(data, ongoingOrder, purchasePrice, trade):
    try:
        currentPrice = data['close'].iloc[-1]
        previousPrice = data['close'].iloc[-2]
        previousLow = data['low'].iloc[-2]
        bolLower = data['Bol_lower'].iloc[-1]
        bolUpper = data['Bol_upper'].iloc[-1]
        ma20 = data['20d_ma'].iloc[-1]
        date = data['date'].iloc[-1]
        thresholdD = bolLower + 0.2 * (ma20 - bolLower)
        thresholdU = bolUpper - 0.2 * (bolUpper - ma20)

        if not ongoingOrder and not maDecreasing(data, 5):
            if touchLowerBB(data, bolLower, 3) and (currentPrice < ma20) and isIncreasing(data, 1):  # price is 20% above lower BB and no ong                                                                                    # price is increasing over the last depth periods
                purchasePrice = currentPrice
                logging.info('buying at {0}'.format(purchasePrice))     
                print 'buying at ', purchasePrice
                printRecord(data)
                return(True, purchasePrice, True)

        if ongoingOrder:              
            if currentPrice < 0.98 * purchasePrice:                                                 # we are losing 5%, stop loss, we close the position
                loss = currentPrice - purchasePrice
                logging.info('sell - closing position - stop loss price {0} loss {1}'.format(currentPrice, loss))
                print 'sell - closing position - stop loss :-( ', currentPrice, loss
                printRecord(data)
                ongoingOrder = False 
                trade = True
                return (ongoingOrder, currentPrice, trade)
                                                                                       
            if (currentPrice > ma20) and touchUpperBB(data, bolUpper, 5) and isDecreasing(data, 2):             # closing position
                profit = currentPrice - purchasePrice
                logging.info('sell price {0} profit {1} '.format(currentPrice, profit))
                print 'sell - hopefully making money here :-) ', currentPrice, profit
                printRecord(data)
                ongoingOrder = False   
                trade = True 
                return (ongoingOrder, currentPrice, trade)                                                                    # closing position
        
        return(ongoingOrder, purchasePrice, trade)

    except Exception, e:
        print 'trade ', str(e)


def isIncreasing(data, depth):     # returns true if the stock price increases the last 'depth' periods
    increasing = False
    count = 0
    i = 0
    while i < depth:
        if data['close'].iloc[-1 - i] > data['close'].iloc[-2 - i]:
            count = count + 1
        i = i + 1
    if count == depth:
        increasing = True                                           
    return increasing


def isDecreasing(data, depth):      # returns true if the stock price decreases the last 'depth' periods
    decreasing = False
    count = 0
    i = 0
    while i < depth:
        if data['close'].iloc[-1 - i] < data['close'].iloc[-2 - i]:
            count = count + 1
        i = i + 1
    if count == depth:
        decreasing = True                                                           
    return decreasing

def touchUpperBB (data, bolUpper, depth):   # returns true if the stock touches the upper Bollinger Band over the last 'depth' periods
    touchUpperBB = False
    i = 0
    while i < depth:
        if data['high'].iloc[-2 - i] >= bolUpper:
            touchUpperBB = True 
        i = i + 1                                                                   
    return touchUpperBB

def touchLowerBB (data, bolLower, depth):   # returns true if the stock touches the lower Bollinger Band over the last 'depth' periods
    touchUpperBB = False
    i = 0
    while i < depth:
        if data['low'].iloc[-2 - i] <= bolLower:
            touchUpperBB = True 
        i = i + 1                                                                   
    return touchUpperBB

def maDecreasing (data, depth):
    decreasing = False
    count = 0
    i = 0
    while i < depth:
        if data['20d_ma'].iloc[-1 - i] < data['20d_ma'].iloc[-2 - i]:
            count = count + 1
        i = i + 1
    if count == depth:
        decreasing = True                                                           
    return decreasing

   


def printRecord(data):
    logging.info('------------RECORD-------------')
    logging.info('close {0} date {1} high {2} low {3} open {4} '.format(data['close'].iloc[-1], \
                                                                        data['date'].iloc[-1], \
                                                                        data['high'].iloc[-1], \
                                                                        data['low'].iloc[-1], \
                                                                        data['open'].iloc[-1]))
    
    logging.info('-------------------')

