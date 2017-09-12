#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, sys
from connect2n import connector

res, i = [], 0
for i in range(12):
    res.append(connector('at&q0' + str(i))[0].decode('utf-8'))
for u in res:
    try:
        i += int((re.search('\) -(.*) dBm', u).group(1)))
    except AttributeError:
        print ('Error while executing data')
        sys.exit(1)
print ('Signal level is: ' + str(round((i/len(res)), 2)) + ' dBm')
