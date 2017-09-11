#!/usr/bin/python
# -*- coding: utf-8 -*-
#https://wiki.2n.cz/btwsgum/latest/en/4-list-of-at-commands/4-2-configuration-commands

import sys,getopt,re
from pduencode import encodeSmsSubmitPdu
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
            sys.exit(1)
    else:
        print(error)
        sys.exit(1)
    
def topdu(num, mes, dcs=0):
    if dcs == 1:
        pdud = encodeSmsSubmitPdu(validnumber(num), mes, sendFlash=True)
    else:
        pdud = encodeSmsSubmitPdu(validnumber(num), mes, sendFlash=False)
    pdu = pdud.replace('0021000AA1', '0001000A81')
    return (pdu)

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
        at = 'at^sg=1,'
    elif sim != 0 and sim <= 6:
        '''SMS to module – request for sending a message via GSM module (in my case 6)'''
        at = 'at^sm=' + str(sim) + ','
    mes = at + str(pdulen(pdu)) + ',' + pdu + ',' + csum(pdu)
    return mes


if __name__ == '__main__':
    
    message = None
    number = None
    flash = None
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hn:m:f",['number=', 'message=', 'flash'])
    except getopt.GetoptError:
        print ('send.py -n <number> -m <message> -f')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('send.py -n <number> -m <message> -f')
            sys.exit(2)
        elif opt in ('-n', '--number'):
            number = arg
        elif opt in ('-m', '--message'):
            message = arg
        elif opt in ('-f', '--flash'):
            flash = 'y'
            
    if number is None: number = validnumber(input("Enter Mobile Number: ")) 
    if message is None: message = str(input("Enter Message: "))
    if flash is None: flash = str(input("Flash Message (y or n): "))
    if flash == 'y':
        dcs = 1
    else:
        dcs = 0
        
    print (nform(topdu(number, message, dcs), sim=1))
##    status = connector((nform(topdu(number, message, dcs), sim=1)), sms=1)
##    if status[0].find('*smsout') == -1:
##        print('Sending sms, please wait')
##        while status[0].find('*smsout') == -1:
##            status = connector((nform(topdu(number, message, dcs), sim=1)), sms=1)
##    print('Sms was sent to ' + number)
