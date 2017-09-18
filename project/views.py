#################
#### imports ####
#################
# -*- coding: utf-8 -*-
from . import app
from flask import render_template, Blueprint, request, redirect, url_for, flash
from .core.send import nform, topdu
from .core.connect2n import connector
from .forms import AddSMSForm

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'info')
 
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send():
    form = AddSMSForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            number = request.form['number']
            message = request.form['message']
            if request.form.get('checkbox'):
                dcs = 1
            else:
                dcs = 0
            status = connector((nform(topdu(number, message, dcs), sim=0)), sms=1)
            if status[0].find('*smsout') == -1:
                flash('Sending sms, please wait')
                while status[0].find('*smsout') == -1:
                    status = connector((nform(topdu(number, message), sim=0)), sms=1)
            flash('Sms was sent to ' + number)
            return render_template('index.html')
        else:
            flash_errors(form)
            flash('ERROR! SMS not send', 'error') 
    return render_template('index.html', form=form)