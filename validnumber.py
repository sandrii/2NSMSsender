#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

def validnumber(num):
    if num[1:].isdigit and 10 < len(num) < 14:
        if len(num) == 9:
            num = '0' + num
            return re.compile('(\+380|380|0380)').sub('0', num)
    else:
        print('Invalid phone number format')


