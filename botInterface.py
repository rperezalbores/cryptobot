'''
Created on Sep 4, 2017

@author: ricardo
'''

filename = 'botConfig.cfg'
fileObj = open(filename)
var = {}
for line in fileObj:
    line = line.strip()
    if not line.startswith('#'):
        key_value = line.split('=')
        if len(key_value) == 2:
            var[key_value[0].strip()] = key_value[1].strip()

var['pair'] = str(var['pair'])
var['exchange'] = str(['exchange'])
start = '01-08-2017 22:01'
end = '01-08-2017 23:01'
var['period'] = int(var['period'])                      


kissLow = 2
kissMA = 3
kissHigh = 3
kissStoploss = 95            

