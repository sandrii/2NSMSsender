from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
 
 
class AddSMSForm(FlaskForm):
    number = StringField('Phone number', validators=[DataRequired()])
    message = StringField('Your message goes here', validators=[DataRequired()])