#!/usr/bin/python
# -*- coding: utf-8 -*-

'''I have old like mammoth shit 2nBluestar gsm gateway https://www.2n.cz with 
horrible, limited functionality GUI, telnet with AT commands.
Example:
        To send sms message   - connector('at^sm=1,13,0001000A81601332547600000168,6e', sms=1)
        To get data from gate - connector('at&spr', 'Layer2')'''

import telnetlib, time

def connector(mes, reunt='OK', sms=0, timeout=1):    
    out = []
    tn = telnetlib.Telnet('172.16.0.11')
    tn.write('\n\r'.encode())
    tn.write('\n\r'.encode())
    tn.read_until('SG login: '.encode())
    tn.write('2n\r'.encode())
    tn.read_until('Password: '.encode())
    tn.write('2n\r'.encode())
    tn.read_until('OK'.encode())
    if sms == 1:
        tn.write('at!g=a6\r'.encode())
        time.sleep(1)
        res = tn.read_very_eager()
        if res.decode('utf-8').find('OK') != -1:
            tn.write((mes + '\r').encode())
            out.append(tn.read_until('*smsout: '.encode()).decode('utf-8'))
            tn.write('at!g=55\r'.encode())
            tn.read_until('OK'.encode())
        elif res.decode('utf-8').find('BUSY') != -1:
            tn.write('at!g=99\r'.encode())
            tn.read_until('OK'.encode())
            tn.write('at!g=a6\r'.encode())
            time.sleep(1)
            res = tn.read_very_eager()
            if res.decode('utf-8').find('OK') != -1:
                tn.write((mes + '\r').encode())
                out.append(tn.read_until('*smsout: '.encode()).decode('utf-8'))
                tn.write('at!g=55\r'.encode())
                tn.read_until('OK'.encode())
    else:
        if timeout > 1:
            tn.write((mes + '\r').encode())
            out.append(tn.read_until(reunt.encode(), timeout))
        else:
            tn.write((mes + '\r').encode())
            out.append(tn.read_until(reunt.encode()))
    tn.close()
    return out
