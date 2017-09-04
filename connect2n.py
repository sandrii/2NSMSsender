#!/usr/bin/python
# -*- coding: utf-8 -*-

'''I have old like mammoth shit 2nBluestar gsm gateway https://www.2n.cz with 
horrible, limited functionality GUI, telnet with AT commands.
Example:
        To send sms message   - connector('at^sm=1,13,0001000A81601332547600000168,6e', sms=1)
        To get data from gate - connector('at&spr', 'Layer2')'''

import telnetlib

def connector(mes, reunt='OK', sms=0):
    tn = telnetlib.Telnet('172.16.0.11')
    tn.write('\n\r'.encode())
    tn.write('\n\r'.encode())
    tn.read_until('SG login: '.encode())
    tn.write('2n\r'.encode())
    tn.read_until('Password: '.encode())
    tn.write('2n\r'.encode())
    tn.read_until('OK'.encode())
    out = []
    if sms == 1:
        '''Activate control via the used session'''
        tn.write('at!g=a6\r'.encode())
        tn.read_until('OK'.encode())
        tn.write((mes + '\r').encode())
        out.append(tn.read_until('*smsout: '.encode()).decode('utf-8'))
        '''Deactivate sms control'''
        tn.write('at!g=55\r'.encode())
        tn.read_until('OK'.encode())
    else:
        tn.write((mes + '\r').encode())
        out.append(tn.read_until(reunt.encode()))
    tn.close()
    return out
