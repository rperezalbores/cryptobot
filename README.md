(more readable using 'raw' format)

This is an experimental bot to trade cryptocurrency. It can also be easily extended to trade regular stocks

bot.py - reads data in real time (mode=realtime) or historic data (mode=history)

bot.py reads the user input data from file botConfig.cfg -it must be in the same directory as bot.py
bot.py uses functions defined in strategy.py

Installation:

Install python
Install pip

Once pip is installed add the following libraries:

pip install matplotlib
pip install numpy
pip install panda

If there are missing dependencies, solve them :-) google is your friend

Preparation:

#botConfig.cfg contains the parameters to model the bot. Modify these as you see fit

pair=USDT_BTC			-> self explanatory. This are Poloniex pairs. Consult Poloniex to see valid pairs
exchange=Poloniex		-> self explanatory
period=300				-> indicates Poloniex period in seconds. For instance selecting 300 (5 minutes) means that Poloniex will return candlesticks with 5 minute data. 
start = '01-08-2017'
end = '02-08-2017'


#Strategies
At the moment only one strategy is implemented. More to be developed.

######---------kissMA----------###### 
#bot purchases when any of the 'kissLow' previous candles lowest price touches the lower BB and the moving average is not decreasing for the last 'kissMA' periods
#bot sells when any of the highest price of the previous 'kissHigh' candles touches the upper BB or if the purchase price is % 'kissStoploss' lower than the current price
#kissMA
kissLow=2
kissMA=3
kissHigh=3
kissStoploss=95


Execution:
python bot_history.py

Results:
Based on the data input and the strategy the bot returns a panda dataframe with the following format  

                   date  index        price     profit  type        xplanation
0   2017-01-07 21:45:00     21   889.701298   0.000000   buy                  
1   2017-01-07 22:20:00     28   898.990000   9.288702  sell  hopefully profit
2   2017-01-08 00:55:00     59   897.000000   0.000000   buy                  
3   2017-01-08 02:40:00     80   915.000000  18.000000  sell  hopefully profit
.....

each one is a dummy trade, indicating timestamp of the transaction, price, operation type and if it is a selling operation, the P&L

Finally provides a summary P&L (hopefull profit) 
Also plots a graph. The index value in the panda dataframe table indicates the candlestick where the transaction took place in the plotted chart. For instance, index 21 indicates that the bot bought at the 21 candlestick in the chart.

[264 rows x 6 columns]
profit 168.75707524


