#!/usr/bin/python
# -*- coding: utf-8 -*-
#https://wiki.2n.cz/btwsgum/latest/en/4-list-of-at-commands/4-2-configuration-commands

import re
from smspdu import SMS_SUBMIT #git@github.com:SAndrii/smspdu.git
from connect2n import connector

def validnumber(num):
    error = 'Invalid phone number format'
    if num[1:].isdigit() and 9 <= len(num) < 14:
        num = re.compile('(\+380|0380|380)').sub('0', num)
        if len(num) == 9:
            num = '0' + num
        try:
            num = re.compile(r'^(?:0)?(50|63|66|67|68|73|91|92|93|94|95|96|97|98|99)\d{7}').match(num).group(0)
            return num
        except AttributeError:
            print(error)
    else:
        print(error)
    
def topdu(num, mes, dcs=0):
    if dcs == 1:
        import unicodedata
        s = unicodedata.name(mes[0]).partition(' ')[0]
        if s == 'CYRILLIC':
            TPDCS = 0x18
        elif s == 'LATIN':
            TPDCS = 0x10
        pdud = SMS_SUBMIT.create(' ', validnumber(num), mes, tp_dcs=TPDCS)
    else:
        pdud = SMS_SUBMIT.create(' ', validnumber(num), mes)
    return ('00' + pdud.toPDU())

def pdulen(l):
    return int(len(l) / 2 - 1)

def csum(l):
    csc = []
    control = 0x0
    for i in range(len(l)):
        if i % 2 == 0:
            continue
        csc.append(l[i - 1] + l[i])
    for i in range(len(csc)):
        control += int(csc[i], 16)
    return hex(control)[-2:]

def nform(pdu, sim=0):
    if sim == 0:
        '''SMS to group – request for sending an SMS message via GSM group'''
        at = 'at^sg=0,'
    elif sim != 0 and sim <= 6:
        '''SMS to module – request for sending a message via GSM module (in my case 6)'''
        at = 'at^sm=' + str(sim) + ','
    mes = at + str(pdulen(pdu)) + ',' + pdu + ',' + csum(pdu)
    return mes

if __name__ == '__main__':
        
    number = str(input('Number:'))
    text = str(input('Message:'))
    #print((nform(topdu(number, text), sim=1)))
    status = connector((nform(topdu(number, text), sim=1)), sms=1)
    if status[0].find('*smsout') == -1:
        print('Sending sms, please wait')
        while status[0].find('*smsout') == -1:
            status = connector((nform(topdu(number, text), sim=1)), sms=1)
    print('Sms was sent to ' + number)
            
