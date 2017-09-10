'''
Created on Sep 4, 2017

@author: ricardo
'''
import time
from dateutil import parser  # covenient lib to manipulate dates

try:
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
    var['exchange'] = str(var['exchange'])
    start = parser.parse(var['start'])              # start is now DateTime format
    var['start'] = time.mktime(start.timetuple())   # now converted into unix time
    end = parser.parse(var['end'])                  # end is now DateTime format
    var['end'] = time.mktime(start.timetuple())     # now converted into unix time
    
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
    var['kissStoploss'] = int(var['kissHigh'])
                 
except Exception, e:
    print 'something wrong on the configuration file: wrong variables ', str(e)

print var
