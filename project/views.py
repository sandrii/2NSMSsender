#################
#### imports ####
#################
# -*- coding: utf-8 -*-

import unicodedata
from time import gmtime, strftime, localtime
from . import app
from flask import render_template, Blueprint, request, redirect, url_for, flash
from .core.send import nform, topdu, validnumber
from .core.connect2n import connector
from .forms import AddSMSForm

def logger(n, m):
    from time import gmtime, strftime, localtime
    stamp = strftime('%d %b %Y %a, %H:%M:%S', localtime())
    return (stamp +  '\t' + n + '\t' + m + '\n')


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash('Error in the {} field - {}'.format(getattr(form, field).label.text, error), 'info')
 
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send():
    form = AddSMSForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            message = request.form['message']
            s = unicodedata.name(message[0]).partition(' ')[0]
            if (s == 'LATIN' and len(message) <= 160) or (s == 'CYRILLIC' and len(message) <=70):
                pass
            else:
                flash('ERROR! message lehght must be less 160 character in english or 70 in cyrrilic ', 'error')
                return render_template('index.html', form=form)
            number = request.form['number']
            if validnumber(number):
                if request.form.get('checkbox'):
                    dcs = 1
                else:
                    dcs = 0
                print (message)
                with open('loger.txt', 'a') as f:
                    f.write(logger(number, message))
                    f.close()
                status = connector((nform(topdu(number, message, dcs), sim=0)), sms=1)
                if status[0].find('*smsout') == -1:
                    flash('Sending sms, please wait', 'info')
                    while status[0].find('*smsout') == -1:
                        status = connector((nform(topdu(number, message), sim=0)), sms=1)
                flash('Sms was sent to ' + number, 'success')
                return render_template('index.html')
            else:
                flash('ERROR! Invalid phone number format', 'error')
        else:
            flash_errors(form)
            flash('ERROR! SMS not send', 'error')
          
    return render_template('index.html', form=form)
