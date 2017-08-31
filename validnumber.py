#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

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
