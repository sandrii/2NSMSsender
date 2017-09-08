import re, sys
from connect2n import connector
'''[b'\r\nat&g3=xtd*112#;\r\n <++g03     atd*112#;\r\n -->g03     OK\r\n -->g03     +CUSD: 2,"ZALYSHOK: 1424:00 HV NA INSHI MEREZHI; 1500 SMS PO UKRAINI; 50:00 HV ZA KORDON']'''


def conto(sim):
    ot = connector('at&g' + str(sim) + '=xtd*112#;', 'KORDON', timeout = 5)
    error = 'SIM card is busy now'
    if ot[0].decode('utf-8').find('BUSY') != -1:
        return error
        sys.exit(2)
    try:
        hv = re.search('OK: (.+?) HV', ot[0].decode('utf-8')).group(1)
        mhv = re.search('NI; (.+?) HV', ot[0].decode('utf-8')).group(1)
        sms = re.search('HI; (.+?) SMS', ot[0].decode('utf-8')).group(1)
        return (hv[:-3], mhv[:-3], sms)
    except AttributeError:
        return error
        sys.exit(2)

for i in range(0,6):
	print(conto(i))
