'''
Created on Sep 2, 2017

@author: ricardo
'''


import logging



def trade(data, ongoingOrder, purchasePrice):
    try:

        currentPrice = data['close'].iloc[-1]
        previousPrice = data['close'].iloc[-2]
        bolLower = data['Bol_lower'].iloc[-1]
        bolUpper = data['Bol_upper'].iloc[-1]
        ma20 = data['20d_ma'].iloc[-1]
        thresholdD = bolLower + 0.2 * (ma20 - bolLower)
        thresholdU = bolUpper - 0.2 * (bolUpper - ma20)

        print currentPrice, bolLower, thresholdD, bolUpper, thresholdU

        if (currentPrice >= thresholdD) and (previousPrice < thresholdD) and (not ongoingOrder):    # price is 20% above lower BB and no ong
            if is_increasing(data, 5):                                                              # price is increasing over the last depth periods
                ongoingOrder = True                                                                 # set order flag
                purchasePrice = currentPrice
                logging.info('buying at ', purchasePrice)                                           # place order

        if ongoingOrder:                                                                            # we have an ongoing order, we need to see when to close
            if purchasePrice <= 0.95 * currentPrice:                                                # we are losing 5%, stop loss, we close the position
                loss = currentPrice - purchasePrice
                logging.info(
                    'sell - closing position - losing money here :-( ', str(loss))
                ongoingOrder = False                                                                        # closing position
            if (currentPrice <= thresholdU) and (previousPrice > thresholdU) and is_decreasing(data, 5):    # price going down
                profit = currentPrice - purchasePrice
                logging.info('sell - making money here :-) ', profit)
                ongoingOrder = False                                                                        # closing position
        return(ongoingOrder, purchasePrice)

    except Exception, e:
        print 'trade ', str(e)


def is_increasing(data, depth):
    increasing = False
    count = 0
    i = 1
    while i <= depth:
        if data['close'].iloc[-1] > data['close'].iloc[-1 - i]:
            count = count + 1
        i = i + 1
    if count == depth:
        increasing = True  # current price is higher than the last depth periods
    return increasing


def is_decreasing(data, depth):
    decreasing = False
    count = 0
    i = 0
    while i < depth:
        i = i + 1
        if data['close'].iloc[-1] < data['close'].iloc[-1 - i]:
            count = count + 1
    if count == depth:
        decreasing = True  # current price is higher than the last depth periods
    return decreasing
