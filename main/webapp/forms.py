from flask_wtf import FlaskForm
from wtforms import *
from wtforms.fields import DateField, TimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from datetime import date

from webapp.models import User

from string import ascii_letters, digits

from datetime import datetime

class SignUpForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired(), Length(min=5, max=20)])
    reg_no = StringField('Registration Number', validators=[DataRequired(), Length(min=10, max=10)])
    dept = SelectField(
        'Department',
        choices=[
            ('Aeronautical', 'Aeronautical'), 
            ('Automobile', 'Automobile'), 
            ('Computer Technology', 'Computer Technology'),
            ('Electronics and Communication', 'Electronics and Communication'),
            ('Information Technology', 'Information Technology'),
            ('Electronics and Instrumentation', 'Electronics and Instrumentation'),
            ('Rubber and Plastic Technology', 'Rubber and Plastic Technology'),
            ('Production Technology', 'Production Technology'),
            ('Artificial Intelligence & Data Science', 'Artificial Intelligence & Data Science'),
            ('Robotics & Automation', 'Robotics & Automation') 
        ],
        validators=[DataRequired()]
    )
    
    
    mobile = StringField('Phone', validators=[DataRequired(), Length(min=10, max=10)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', "Password doesn't match")])

    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Account already exists')
    
    def validate_reg_no(self, reg_no):
        try:
            print(reg_no)
            int(reg_no.data)
        except:
            raise ValidationError('Invalid Registration Number')
        user = User.query.filter_by(reg_no=reg_no.data).first()
        if user:
            raise ValidationError('Account already exists')

    def validate_mobile(self, mobile):
        try:
            n = int(mobile.data)
        except:
            raise ValidationError('Invalid Mobile Number')

        
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Get Reset Link')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('No such account exists')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', "Password doesn't match")])

    submit = SubmitField('Reset')


class AdminForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')