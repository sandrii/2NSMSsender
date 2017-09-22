from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

 
class AddSMSForm(FlaskForm):
    number = StringField('Phone number', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])